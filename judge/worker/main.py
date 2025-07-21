from model import getSession,Submission
from redis import get_next,connection
import os
#testing remains for all worker logic


cgState="" #using till memory.events issue gets resolved

class Files:
    def __init__(self,boxid,workdir,dir,src,stdin,stdout,stderr,stdresult,metadata):
        self.boxid = boxid
        self.workdir = workdir
        self.dir=dir
        self.src=src
        self.stdin=stdin
        self.stdout=stdout
        self.stderr=stderr
        self.stdresult=stdresult
        self.metadata=metadata


def writefile(filename,content):

    os.system(f"touch {filename} && chown $(whoami) {filename}")
    os.system(f"chmod +x {filename}")
    with open(f"{filename}",'w') as f:
        f.write(content)

def readFile(filename):
    with open(filename,'r') as f:
        output=f.read().strip()
    return output
    

def parseFile(filename):
    content={}
    with open(filename,'r') as f:
        
        for line in f:
            if ":" in line:
                key,value=line.strip().split(":",1)
                content[key.strip()]=value.strip()
    return content

def initialize_files(sub):
    boxid=int(sub.id%(10e7))
    workdir=f"/var/lib/isolate/{boxid}"
    dir=workdir+"/box"
    stdin=workdir+"/stdin"
    stdout=workdir+"/stdout"
    stderr=workdir+"/stderr"
    stdresult=workdir+"/stdresult"
    metadata=workdir+"/metadata"

    os.system(f"isolate -b {boxid} {cgState} --init")
    writefile(stdin,sub.input)
    writefile(stdout,"")
    writefile(metadata,"")
    writefile(stdresult,sub.exp_result)

    if sub.language=="python":
        src=dir+"/app.py"
    if sub.language=="cpp":
        src=dir+"/app.cpp"

    print(src)
    writefile(src,sub.src)

    return Files(boxid,workdir,dir,src,stdin,stdout,stderr,stdresult,metadata)


def compile(sub,files):
    if(sub.language=="python"):
        return
    
    comp_sc=""
    if(sub.language=="cpp"):
        comp_sc=f"/usr/bin/g++ -o app app.cpp"
    
    compile_output=files.workdir+"/compile_output.txt"
    writefile(compile_output,"")

    #compile_sc=dir+"/compile"
    command=f"isolate -b {files.boxid} {cgState} -p5  -E PATH=\"/bin:/usr/bin\" --run -- {comp_sc} 2>{compile_output} "
    os.system(command)

    output=readFile(compile_output)
    print(output)
    return output


def run(sub,files):

    if(sub.language=="python"):
        run="/usr/bin/python3 app.py"
    else:
        run="app"
    
    command=f"isolate -b {files.boxid} -s {cgState} \
        -M {files.metadata} \
        -t {sub.timeLimit} \
        -w {sub.timeLimit} \
        -x 0 \
        -m {sub.memLimit} \
        -p1 \
        -f 10000 \
        -E PATH=\"/bin:/usr/bin\" \
        --run -- {run} <{files.stdin} >{files.stdout} 2>{files.stderr}"

    os.system(command)

    return



def getError(status):
    print(status)
    if(status=="TO"):
        return "time limit exceeded"
    elif(status=="SG" or status=="RE"):
        print(status)
        return "runtime error"  
    elif(status=="XX"):
        return "internal error"
    else:
        return "unknown error"



def verify(sub,files):

    metadata=parseFile(files.metadata)

    sub.time=metadata["time"]
    sub.memory=metadata["max-rss"]

    sub.output=readFile(files.stdout)
    print(readFile(files.stderr))
    if("status" in metadata):
        sub.status=getError(metadata["status"])
    elif(readFile(files.stderr)):
        sub.status="wrong answer"
        sub.output=readFile(files.stderr)
    elif(sub.output==sub.exp_result):
        sub.status="accepted"
    else:
        sub.status="wrong answer"


    return

def clean(files):
    os.system(f"isolate -b {files.boxid} {cgState} --cleanup")
    return


def execute(db_session,redconn):
    subid=get_next(redconn)
    if subid==None:
        return
    #db_session=getSession()
    sub=db_session.query(Submission).filter_by(id=int(subid)).first()
    sub.status="running"
    db_session.commit()

    files=initialize_files(sub)

    compile_output=compile(sub,files)

    if compile_output and "OK" not in compile_output:
        sub.status="compilation error"
        sub.output=compile_output
        db_session.commit()
        return 
    
    run(sub,files)
    print("done")
    
    verify(sub,files)
    
    clean(files)

    db_session.commit()



if __name__=="__main__":
    db_session=getSession()
    redconn=connection()
    while True:
        execute(db_session,redconn)
        





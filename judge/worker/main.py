from .model import getSession,Submission
from .redis import get_next
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

    os.system(f"touch {filename} && chown $whoami {filename}")
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
            key,value=line.strip(":",1)
            content[key]=value
    return content

def initialize_files(sub):
    boxid=sub.id%(10e7)
    workdir="/var/lib/isolate/{boxid}"
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

    if sub.lang=="python":
        src=dir+"/app.py"
    if sub.lang=="cpp":
        src=dir+"/app.cpp"

    writefile(src,sub.src)

    return Files(boxid,workdir,dir,src,stdin,stdout,stderr,stdresult,metadata)


def compile(sub,files):
    if(sub.language=="python"):
        return
    
    comp_sc=""
    if(sub.language=="cpp"):
        comp_sc=f"g++ -o app {files.src}"
    
    compile_output=files.workdir+"/compile_output.txt"
    writefile(compile_output,"")

    compile_sc=dir+"/compile"
    command=f"isolate -b {files.boxid} {cgState} -p 5  -E PATH=\"/bin:/usr/bin\" --run -- {comp_sc} > {compile_output} "
    os.system(command)

    output=readFile(compile_output)

    return output


def run(sub,files):

    if(sub.language=="python"):
        run="/usr/bin/python3 run.py"
    else:
        run="/bin/bash run"
    
    command=f"isolate -b {files.boxid} -s {cgState} \
        -M {files.metadata} \
        -t {sub.timeLimit} \
        -w {sub.timeLimit} \
        -x 0 \
        -m {sub.memLimit} \
        -p 1 \
        -f 10000 \
        -E PATH=\"/bin:/usr/bin\" \
        --run -- {run} <{files.stdin} >{files.stdout} 2>{files.stderr}"

    os.system(command)

    return



def getError(status):

    if(status=="TO"):
        return "time limit exceeded"
    elif(status=="SG" or status=="RE"):
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
    os.system(f"isolate -b {files.boxid} --cg --cleanup")
    return


def execute(db_session):
    subid=get_next()
    if subid==None:
        return
    #db_session=getSession()
    sub=db_session.query(Submission).filter_by(id=subid).first()
    sub.status="running"
    db_session.commit()

    files=initialize_files(sub)

    compile_output=compile(sub,files)

    if compile_output:
        sub.status="compilation error"
        sub.output=compile_output
        db_session.commit()
        return 
    
    run(sub,files)
    
    verify(sub,files)
    
    clean(files)

    db_session.commit()



if __name__=="__main__":
    
    while True:
        db_session=getSession()
        execute(db_session)





from .model import getSession,Submission
from .redis import get_next
import os
#testing remains for all worker logic

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


def initialize_files(sub):
    boxid=sub.id%(10e7)
    workdir="/var/lib/isolate/{boxid}"
    dir=workdir+"/box"
    stdin=workdir+"/stdin"
    stdout=workdir+"/stdout"
    stderr=workdir+"/stderr"
    stdresult=workdir+"/stdresult"
    metadata=workdir+"/metadata"

    os.system("isolate -b {boxid} --cg --init")
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
    command=f"isolate -b {files.boxid} --cg -p 1000 --run {comp_sc} > {compile_output} "
    os.system(command)

    with open(compile_output,'r') as f:
        output=f.read().strip()

    return output


def run(sub,files):

    if(sub.language=="python"):
        run="/usr/bin/python3 run.py"
    else:
        run="/bin/bash run"
    
    command=f"isolate -b {files.boxid} -s --cg \
        -M {files.metadata} \
        -t {sub.timeLimit} \
        -w {sub.timeLimit} \
        -x 0 \
        -m {sub.memLimit} \
        -p 5 \
        -f 10000 \
        -E PATH=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\" \
        --run {run} <{files.stdin} >{files.stdout} 2>{files.stderr}"

    os.system(command)

    return


def verify(sub,files):
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





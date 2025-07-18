from .model import getSession,Submission
from .redis import get_next
import os

def writefile(filename,content):

    os.system("touch {fileanam} && chown $whoami {filename}")

    with open("{filename}",'w') as f:
        f.write(content)


def initialize_files(submissionid):
    boxid=submissionid%(10e7)
    workdir="/var/lib/isolate/{boxid}"
    dir=workdir+"/box"
    stdin=workdir+"/stdin"
    stdout=workdir+"/stdout"
    stderr=workdir+"/stderr"
    metadata=workdir+"/metadata"
    cmpr=dir+"/cmpr"

    os.system("isolate -b {boxid} --cg --init")
    writefile(stdin," ")
    writefile(stdout," ")
    writefile(metadata," ")

    cmpr_cont=f'#!/bin/bash /n if cmp -s "$1" "$2" ;then exit 0 else  exit 1 fi'

    writefile(cmpr,content=cmpr_cont)

    return dir,stdin,stdout,stderr,metadata


def compile(lang,dir,metadata):
    if(lang=="python"):
        return 

    comp_sc=""

    if(lang=="cpp"):
        comp_sc="g++ -o app app.cpp"


def run():
    return


def main():
    subid=get_next()
    db_session=getSession()
    
    sub=db_session.query(Submission).filter_by(id=subid).first()
    sub.status="running"
    db_session.commit()

    dir,stdin,stdout,stderr,metadata=initialize_files(subid)

    compite_output=compile(sub.language,dir,metadata=metadata)





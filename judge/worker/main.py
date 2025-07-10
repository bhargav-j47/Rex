from .model import getSession,Submission
from .redis import get_next


def writefile(filename,content):
    with open(filename,'w') as f:
        f.write(content)



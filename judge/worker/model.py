import urllib.parse
import sqlalchemy as db
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker,declarative_base

load_dotenv(dotenv_path='./.env')

name=os.getenv('POSTGRES_NAME')
username=os.getenv('POSTGRES_USERNAME')
password=os.getenv('POSTGRES_PASSWORD')
host=os.getenv('POSTGRES_HOST')
port=os.getenv('POSTGRES_PORT')
password=urllib.parse.quote_plus(password)
conn_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{name}"

Base = declarative_base()
class Submission(Base):
    __tablename__ = 'Submission'
    id = db.Column(db.Integer, primary_key=True)
    language=db.Column(db.String)
    input=db.Column(db.String)
    exp_result=db.Column(db.String)
    output=db.Column(db.String)
    status=db.Column(db.String)
    src=db.Column(db.String)
    time=db.Column(db.Integer)
    memory=db.Column(db.Integer)
    setLimit=db.Column(db.String)
    timeLimit=db.Column(db.Integer)
    memLimit=db.Column(db.Integer)


def getSession():
    engine =db.create_engine(conn_string)
    Session = sessionmaker(bind=engine)
    session=Session()
    return session
"""
def get(id):
    session=getSession()
    sub=session.query(Submission).filter_by(id=id).first()
    sub=update(sub,"done","12",44,256)
    session.commit()
    print(sub.status,sub.id)
    return sub

def update(sub,status,output,time,memory):
    sub.status=status
    sub.output=output
    sub.time=time
    sub.memory=memory

    return sub
    

s=get(2)
"""

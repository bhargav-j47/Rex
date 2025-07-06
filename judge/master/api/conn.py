import valkey
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
HOST=os.getenv("VALKEY_HOST")
PORT=os.getenv('VALKEY_PORT')


def connection():

    try:
        return valkey.Redis(host=HOST, port=int(PORT), db=0)
    except:
        return "error"
    

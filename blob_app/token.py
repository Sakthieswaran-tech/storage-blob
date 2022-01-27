from datetime import datetime,timedelta
from .schemas import TokenDetails
from jose import JWTError,jwt
from typing import Optional

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ID=None

def create_access_token(data:dict):
    expire=datetime.utcnow()+timedelta(minutes=15)
    data.update({"exp":expire})
    access_token=jwt.encode(data,SECRET_KEY,ALGORITHM)
    return access_token

def token_verify(token:str,login_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,ALGORITHM)
        name:str=payload.get("name")
        id:int=payload.get("id")
        print("token id ",id)
        if name is None:
            raise login_exception
        token_data=TokenDetails(username=name,id=id)
    except JWTError:
        raise login_exception

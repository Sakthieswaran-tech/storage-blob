import email
from os import path
from typing import List, Optional
from pydantic import BaseModel

class ShowUser(BaseModel):
    username:str
    email:str
    password:str

class User(BaseModel):
    id:int
    username:str
    email:str
    class Config():
        orm_mode=True

class Login(BaseModel):
    username:str
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenDetails(BaseModel):
    username:Optional[str]=None
    id:Optional[int]=None

class UploadFile(BaseModel):
    path:str

class ShowFile(BaseModel):
    id:int
    path:str
    class Config():
        orm_mode=True

class ShowAllFile(BaseModel):
    username:str
    email:str
    files:List[ShowFile]=[]
    class Config():
        orm_mode=True


class ShowFileDetails(BaseModel):
    id:int
    path:str
    size:int
    file_name:str
    file_type:str
    creator:User
    class Config():
        orm_mode=True


from sqlalchemy import Column, ForeignKey,String,Integer
from .database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String)
    password=Column(String)
    email=Column(String)
    files=relationship("File",back_populates="creator")

class File(Base):
    __tablename__="files"
    id=Column(Integer,primary_key=True,index=True)
    file_name=Column(String)
    path=Column(String)
    owner=Column(Integer,ForeignKey("users.id"))
    size=Column(Integer)
    file_type=Column(String)
    creator=relationship("User",back_populates="files")
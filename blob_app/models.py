from sqlalchemy import Column, ForeignKey,String,Integer
from .database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String)
    password=Column(String)
    email=Column(String)
    files=relationship("Files",back_populates="creator")

class Files(Base):
    __tablename__="files"
    id=Column(Integer,primary_key=True,index=True)
    file_name=Column(String)
    path=Column(String)
    owner=Column(Integer,ForeignKey("users.id"))
    size=Column(Integer)
    file_type=Column(String)
    creator=relationship("User",back_populates="files")
    shared_file=relationship("FileSharing",back_populates="shared")

class FileSharing(Base):
    __tablename__="filesharing"
    id=Column(Integer,primary_key=True,index=True)
    file_id=Column(Integer,ForeignKey("files.id"))
    shared=relationship("Files",cascade="all,delete",back_populates="shared_file")
    owner_id=Column(Integer,ForeignKey("users.id"))
    shared_users=Column(Integer,ForeignKey("users.id"))
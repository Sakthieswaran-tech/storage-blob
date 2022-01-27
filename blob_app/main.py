from base64 import decode
import os
from sre_constants import MAGIC
from fastapi.responses import FileResponse
from typing import List
from fastapi import Depends, FastAPI, File,HTTPException, Path, status,UploadFile
from . import schemas
from sqlalchemy.orm import Session
from .database import get_db,engine
from . import models
from .hashing import Hash
from fastapi.security import OAuth2PasswordRequestForm
from .token import create_access_token,SECRET_KEY,ALGORITHM
from .oauth2 import current_user
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
import shutil

app=FastAPI()

models.Base.metadata.create_all(engine)
oauth2=OAuth2PasswordBearer(tokenUrl="login")

@app.post("/user")
def create_user(request:schemas.ShowUser,db:Session=Depends(get_db),get_current_user:schemas.ShowUser=Depends(current_user)):
    new_user=models.User(
        username=request.username,
        password=Hash.bcrypt(request.password),
        email=request.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
async def login(request:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.username==request.username).first()
    print(user.id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid username"
        )

    if not Hash.verify(user.password,request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    access_token=create_access_token(data={"name":user.username,"id":user.id})
    return {"access_token":access_token,"token_type":"bearer"}

@app.get("/users",response_model=schemas.User)
def get_user(token:str=Depends(oauth2),db:Session=Depends(get_db),get_current_user:schemas.ShowUser=Depends(current_user)):
    decoded=jwt.decode(token,SECRET_KEY,ALGORITHM)
    name:str=decoded.get("name")
    print(token)
    print(name)
    user=db.query(models.User).filter(models.User.username==name).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not allowed"
        )
    return user
    
@app.get("/allusers",response_model=List[schemas.User])
def get_all(db:Session=Depends(get_db)):
    user=db.query(models.User).all()
    return user

@app.post("/files")
def upload_file(token:str=Depends(oauth2),file:UploadFile=File(...),db:Session=Depends(get_db),get_current_user:schemas.ShowUser=Depends(current_user)):
    decoded=jwt.decode(token,SECRET_KEY,ALGORITHM)
    id:int=decoded.get("id")
    file_location=f"uploads/{file.filename}"
    with open(file_location,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)
    size=os.path.getsize(file_location)
    print(size)
    file_upload=models.File(path=file_location,owner=id,size=size,file_type=file.content_type,file_name=file.filename)
    db.add(file_upload)
    db.commit()
    db.refresh(file_upload)
    return {"result":"Success","Obj":file_upload}

@app.get("/files",response_model=schemas.ShowAllFile)
def download_file(token:str=Depends(oauth2),db:Session=Depends(get_db),get_current_user:schemas.ShowUser=Depends(current_user)):
    decoded=jwt.decode(token,SECRET_KEY,ALGORITHM)
    username:str=decoded.get("name")
    id:int=decoded.get("id")
    user_details=db.query(models.User).filter(models.User.id==id).first()
    if user_details is None:
        return "Not found"
    return user_details

@app.get("/files/{id}")
def download_single(id:int,token:str=Depends(oauth2),db:Session=Depends(get_db),get_current_user:schemas.ShowUser=Depends(current_user)):
    if token is None:
        return "No token"
    decoded=jwt.decode(token,SECRET_KEY,ALGORITHM)
    owner:int=decoded.get("id")
    print("owner ",owner)
    get_file_id=db.query(models.File).filter(models.File.id==id).first()
    print("file id ",get_file_id.id,"   owner id ",get_file_id.owner)
    if get_file_id.owner!=owner:
        return "Not allowed"
    return FileResponse(path=get_file_id.path,media_type=get_file_id.file_type,filename=get_file_id.file_name)



@app.delete("/files/{id}")
def delete_file(id:int,db:Session=Depends(get_db)):
    del_file=db.query(models.File).filter(models.File.id==id).first()
    if del_file is None:
        return "file does not exist"
    if os.path.exists(del_file.path):    
        os.remove(del_file.path)
        db.query(models.File).filter(models.File.id==del_file.id).delete(synchronize_session=False)
        db.commit()
        return f"{id} deleted"
    else:
        return "Path no"

@app.get("/tokendetails")
def token_detail(token:str=Depends(oauth2),db:Session=Depends(get_db),get_current_user:schemas.ShowUser=Depends(current_user)):
    decoded=jwt.decode(token,SECRET_KEY,ALGORITHM)
    username=decoded.get("name")
    id=decoded.get("id")
    return{"name":username,"id":id}

@app.get("/allfiles")
def file_details(db:Session=Depends(get_db)):
    details=db.query(models.File).all()
    return details

# @app.put("/files/{id}")
# def rename_file(id:int,request,db:Session=Depends(get_db)):
#     cur=db.query(models.File).filter(models.File.id==id).first()
#     if cur is None:
#         return "File does not exist"
#     path=cur.path.split('/')[1]
#     cur.path.up= os.rename(path,request.newname)
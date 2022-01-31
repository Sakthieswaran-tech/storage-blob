from fastapi import Depends,UploadFile,File,HTTPException,status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from blob_app import schemas
from ..database import get_db
import shutil
from jose import jwt
import os
import gzip
from ..models import FileSharing,User,Files
from ..authentications.token import SECRET_KEY,ALGORITHM

def upload_file(token:str,db:Session=Depends(get_db),file:UploadFile=File(...)):
    decoded=jwt.decode(token,SECRET_KEY,ALGORITHM)
    id:int=decoded.get("id")
    file_location=f"uploads/{file.filename}"
    with open(file_location,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)
    size=os.path.getsize(file_location)
    file_upload=Files(path=file_location,owner=id,size=size,file_type=file.content_type,file_name=file.filename)
    db.add(file_upload)
    db.commit()
    db.refresh(file_upload)
    return {"result":"Success","Obj":file_upload}

def download_file(id:int,token:str,db:Session=Depends(get_db)):
    shared_info=db.query(FileSharing).filter(FileSharing.file_id==id).all()
    my_list=[]
    if len(shared_info)!=0:
        for i in range(0,len(shared_info)):
            my_list.append(shared_info[i].shared_users)
    if token is None:
        return "No token"
    decoded=jwt.decode(token,SECRET_KEY,ALGORITHM)
    owner:int=decoded.get("id")
    print("owner ",owner)
    get_file=db.query(Files).filter(Files.id==id).first()
    print("file id ",get_file.id,"   owner id ",get_file.owner)
    if get_file.owner!=owner and owner not in my_list:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not allowed"
        )
    return FileResponse(path=get_file.path,media_type=get_file.file_type,filename=get_file.file_name)

def delete_file(id:int,token:str,db:Session=Depends(get_db)):
    decoded=jwt.decode(token,SECRET_KEY,ALGORITHM)
    owner:int=decoded.get("id")
    get_file_id=db.query(Files).filter(Files.id==id).first()
    if get_file_id is None:
        return "File not found"
    if get_file_id.owner!=owner:
        return "Not allowed"
    if os.path.exists(get_file_id.path):    
        os.remove(get_file_id.path)
        db.query(Files).filter(Files.id==id).delete(synchronize_session=False)
        db.commit()
        return f"{id} deleted"
    else:
        return "Path not found"

def share_file(id:int,request,token:str,db:Session=Depends(get_db)):
    decoded=jwt.decode(token,SECRET_KEY,ALGORITHM)
    owner:int=decoded.get("id")
    print("owner ",owner)
    get_file_id=db.query(Files).filter(Files.id==id).first()
    if get_file_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File not found"
        )
    if get_file_id.owner!=owner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not allowed"
        )
    for i in range(0,len(request.username)):
        user_detail=db.query(User).filter(User.username==request.username[i]).first()
        if user_detail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        shared_details=FileSharing(file_id=id,owner_id=owner,shared_users=user_detail.id)
        db.add(shared_details)
        db.commit()
        db.refresh(shared_details)
    return "File shared successfully"

def compress(id:int,token:str,db:Session=Depends(get_db)):
    decoded=jwt.decode(token,SECRET_KEY,ALGORITHM)
    owner:int=decoded.get("id")
    fileresp=db.query(Files).filter(Files.id==id).first()
    if fileresp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    if fileresp.owner!=owner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not allowed to access this file"
        ) 
    with open(fileresp.path,"rb") as f_in:
        with gzip.open(f"{fileresp.path}.gz","wb") as out:
            shutil.copyfileobj(f_in,out)
    return FileResponse(path=f"{fileresp.path}.gz",media_type="application/tar",filename=f"{fileresp.file_name}.gz")

def rename_file(id:int,token:str,request:schemas.RenameFile,db:Session=Depends(get_db)):
    decoded=jwt.decode(token,SECRET_KEY,ALGORITHM)
    ids:int=decoded.get("id")
    file=db.query(Files).filter(Files.id==id)
    if not file.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    if ids!=file.first().owner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not allowed"
        )
    filetype=file.first().file_type.split("/")[1]
    os.rename(file.first().path,f"uploads/{request.filename}.{filetype}")
    file.update({"path":f"uploads/{request.filename}.{filetype}","owner":ids,"size":file.first().size,"file_type":file.first().file_type,"file_name":request.filename},synchronize_session=False)
    db.commit()
    return "changed"
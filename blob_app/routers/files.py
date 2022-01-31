from fastapi import APIRouter,status,Depends,UploadFile,File,HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas
from ..authentications.oauth2 import current_user
from fastapi.requests import Request
from ..repository import files
from jose import jwt
router=APIRouter(
    prefix="/files",
    tags=["Files"]
)
oauth2=OAuth2PasswordBearer(tokenUrl="login")

@router.post("/",status_code=status.HTTP_200_OK)
def upload_file(request:Request,token:str=Depends(oauth2),file:UploadFile=File(...),db:Session=Depends(get_db),get_current_user:schemas.ShowUser=Depends(current_user)):
    return files.upload_file(token,db,file)
    

@router.get("/{id}",status_code=status.HTTP_200_OK)
def download_file(id:int,token:str=Depends(oauth2),db:Session=Depends(get_db),get_current_user:schemas.ShowUser=Depends(current_user)):
    return files.download_file(id,token,db)
    

@router.delete("/{id}",status_code=status.HTTP_200_OK)
def delete_file(id:int,token:str=Depends(oauth2),db:Session=Depends(get_db),get_current_user:schemas.ShowUser=Depends(current_user)):
    return files.delete_file(id,token,db)
    

@router.post("/share/{id}",status_code=status.HTTP_200_OK)
def share_file(id:int,request:schemas.ShareOneFile,token:str=Depends(oauth2),db:Session=Depends(get_db),get_current_user:schemas.ShowUser=Depends(current_user)):
    return files.share_file(id,request,token,db)
    

@router.get("/compress/{id}",status_code=status.HTTP_200_OK)
def compress(id:int,db:Session=Depends(get_db),token:str=Depends(oauth2),get_current_user:schemas.ShowUser=Depends(current_user)):
    return files.compress(id,token,db)
    
@router.put("/rename/{id}",status_code=status.HTTP_200_OK)
def rename(id:int,request:schemas.RenameFile,db:Session=Depends(get_db),token:str=Depends(oauth2),get_current_user:schemas.ShowUser=Depends(current_user)):
    return files.rename_file(id,token,request,db)
    
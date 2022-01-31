from fastapi import APIRouter,status,Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas
from fastapi.security import OAuth2PasswordBearer
from ..authentications.oauth2 import current_user
from ..repository import users

oauth2=OAuth2PasswordBearer(tokenUrl="login")


router=APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/",status_code=status.HTTP_201_CREATED)
def create_user(request:schemas.ShowUser,db:Session=Depends(get_db)):
    return users.create_user(request,db)
    
@router.get("/",response_model=schemas.User)
def get_user(token:str=Depends(oauth2),db:Session=Depends(get_db),get_current_user:schemas.ShowUser=Depends(current_user)):
    return users.get_user(token,db)
    

@router.delete("/",status_code=status.HTTP_404_NOT_FOUND)
def delete_user(token:str=Depends(oauth2),db:Session=Depends(get_db),get_current_user:schemas.ShowUser=Depends(current_user)):
    return users.delete_user(token,db)
    
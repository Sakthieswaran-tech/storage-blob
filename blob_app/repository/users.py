from fastapi import Depends,HTTPException,status
from sqlalchemy.orm import Session
from .. import models
from blob_app.database import get_db
from ..authentications.token import ALGORITHM,SECRET_KEY
from ..authentications.hashing import Hash
from jose import jwt


def create_user(request,db:Session=Depends(get_db)):
    new_user=models.User(
        username=request.username,
        password=Hash.bcrypt(request.password),
        email=request.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user(token:str,db:Session=Depends(get_db)):
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

def delete_user(token:str,db:Session=Depends(get_db)):
    decoded=jwt.decode(token,SECRET_KEY,ALGORITHM)
    id=decoded.get("id")
    db.query(models.User).filter(models.User.id==id).delete(synchronize_session=False)
    db.commit()
    return "user deleted"
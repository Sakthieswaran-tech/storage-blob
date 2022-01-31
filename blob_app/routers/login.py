from fastapi import status,APIRouter,HTTPException,Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..authentications.hashing import Hash
from ..authentications.token import create_access_token,SECRET_KEY,ALGORITHM


router=APIRouter(
    prefix="/login",
    tags=["Log-in"]
)

@router.post("/",status_code=status.HTTP_200_OK)
def login(request:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.username==request.username).first()
    print(user.username)
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
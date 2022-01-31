from fastapi import Depends,HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .token import token_verify


oauth2=OAuth2PasswordBearer(tokenUrl="login")

def current_user(token:str=Depends(oauth2)):
    login_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )
    return token_verify(token,login_exception)
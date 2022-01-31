from .database import engine
from fastapi.exceptions import RequestValidationError
from . import models
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from .routers import users,login,files

app=FastAPI()

models.Base.metadata.create_all(engine)
oauth2=OAuth2PasswordBearer(tokenUrl="login")

app.include_router(users.router)
app.include_router(login.router)
app.include_router(files.router)



    
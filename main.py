# fastapi template for authentication with firebase (pyrebase4 package)

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pyrebase import pyrebase
import os
import uvicorn
from dotenv import load_dotenv

# fastapi initialization
app = FastAPI()
load_dotenv()

# User model
class User(BaseModel):
    email: str
    password: str
    display_name: str

# add display_name to the user model
class ExtendedOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    display_name: str

# firebase config
config = {
    "apiKey": os.getenv("apiKey"),
    "authDomain": os.getenv("authDomain"),
    "databaseURL": os.getenv("databaseURL"),
    "projectId": os.getenv("projectId"),
    "storageBucket": os.getenv("storageBucket"),
    "messagingSenderId": os.getenv("messagingSenderId"),
    "appId": os.getenv("appId"),
    "measurementId": os.getenv("measurementId"),
}

# firebase initialization
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

@app.post("/create_user")
async def create_user(user: User):
    try:
        user = auth.create_user_with_email_and_password(user.email, user.password)
        user = auth.update_profile(user, {"displayName": user.display_name})
        return user
    except Exception as e:
        return {"error": "Something went wrong", "message": str(e)}

@app.post("/login")
async def login(form_data: ExtendedOAuth2PasswordRequestForm = Depends()):
    try:
        user = auth.sign_in_with_email_and_password(form_data.username, form_data.password)
        return user
    except Exception as e:
        return {"error": "Something went wrong", "message": str(e)}

@app.post("/logout")
async def logout():
    try:
        user = auth.current_user
        auth.current_user = None
        return user
    except Exception as e:
        return {"error": "Something went wrong", "message": str(e)}

@app.get("/")
async def root():
    # if user is logged in
    if auth.current_user:
        return auth.current_user
    # if user is not logged in
    else:
        # render login page
        return {"error": "You are not logged in"}

# run the app
if __name__ == "__main__":
    uvicorn.run(app)


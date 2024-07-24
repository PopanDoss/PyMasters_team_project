from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException
from passlib.context import CryptContext

from sqlalchemy.orm import Session
from jose import JWTError, jwt
from starlette import status

from pymasters.database.models import User
from pymasters.database.db import get_db

from pymasters.settings import SECRET_KEY, ALGORITHM, oauth2_scheme

class Hash:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    def verify_password(self, plain_password, hashed_password):
  
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
      
        return self.pwd_context.hash(password)



def create_access_token(data: dict, expires_delta: Optional[float] = None):

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"})
    encoded_access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_access_token


def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
  
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(datetime.UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"})
    encoded_refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token


def get_email_form_refresh_token(refresh_token: str):

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['scope'] == 'refresh_token':
            email = payload['sub']
            return email
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload['scope'] == 'access_token':
            email = payload["sub"]
            exp = payload['exp']
            if email is None:
                raise credentials_exception
            if exp is None or exp <= int(datetime.now(timezone.utc).timestamp()):
                raise HTTPException( 
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="JWT Token expired",
                    headers={"WWW-Authenticate": "Bearer"})
        else:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user: User = db.query(User).filter(User.email == email).first()
    if user is None :
        raise credentials_exception
    return user

# Функції для перевірки ролей користувачів 
async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")
    return current_user

async def get_moderator_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")
    return current_user
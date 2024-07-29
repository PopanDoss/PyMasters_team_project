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
    """
    A class for hashing and verifying passwords using bcrypt.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies that a plain password matches a hashed password.
        
        Args:
            plain_password (str): The plain password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)


    def get_password_hash(self, password: str) -> str:
        """
        Hashes a password.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[float] = None) -> str:
    """
    Creates a JWT access token.

    Args:
        data (dict): The data to include in the token.
        expires_delta (Optional[float]): The token's lifespan in seconds. Defaults to 15 minutes if not provided.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"})
    encoded_access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_access_token


def create_refresh_token(data: dict, expires_delta: Optional[float] = None) -> str:
    """
    Creates a JWT refresh token.

    Args:
        data (dict): The data to include in the token.
        expires_delta (Optional[float]): The token's lifespan in seconds. Defaults to 7 days if not provided.

    Returns:
        str: The encoded JWT refresh token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"})
    encoded_refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token


def get_email_form_refresh_token(refresh_token: str) -> str:
    """
    Extracts the email from a JWT refresh token.

    Args:
        refresh_token (str): The JWT refresh token.

    Returns:
        str: The email embedded in the token.

    Raises:
        HTTPException: If the token is invalid or has an incorrect scope.
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['scope'] == 'refresh_token':
            email = payload['sub']
            return email
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Retrieves the current user based on the provided JWT access token.

    Args:
        token (str): The JWT access token.
        db (Session): The database session.

    Returns:
        User: The user corresponding to the token.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
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
    except JWTError:
        raise credentials_exception

    user: User = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensures that the current user is an admin.

    Args:
        current_user (User): The current user.

    Returns:
        User: The current user if they are an admin.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")
    return current_user


async def get_moderator_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensures that the current user is a moderator or admin.

    Args:
        current_user (User): The current user.

    Returns:
        User: The current user if they are a moderator or admin.

    Raises:
        HTTPException: If the user is not a moderator or admin.
    """
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")
    return current_user

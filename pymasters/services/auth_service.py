from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from starlette import status

from pymasters.settings import SECRET_KEY, ALGORITHM

def create_email_token(data: dict, SECRET_KEY=SECRET_KEY, ALGORITHM=ALGORITHM):
    """
    Create a JWT token for email verification.

    Args:
        data (dict): Data to encode in the JWT.
        SECRET_KEY (str): Secret key for encoding the JWT.
        ALGORITHM (str): Algorithm for encoding the JWT.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

async def get_email_from_token(token: str, SECRET_KEY=SECRET_KEY, ALGORITHM=ALGORITHM):
    """
    Decode the JWT token and extract the email address.

    Args:
        token (str): The JWT token to decode.
        SECRET_KEY (str): Secret key for decoding the JWT.
        ALGORITHM (str): Algorithm for decoding the JWT.

    Returns:
        str: The extracted email address.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Token does not contain email address")
        return email
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Invalid token for email verification") from e

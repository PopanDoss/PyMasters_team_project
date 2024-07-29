
import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException
from starlette import status

from pymasters.services.auth_service import create_email_token, get_email_from_token
from pymasters.settings import SECRET_KEY, ALGORITHM

@pytest.fixture(scope="function")
def test_email():
    return "test@example.com"

@pytest.fixture(scope="function")
def test_token(test_email):
    return create_email_token({"sub": test_email})

def test_create_email_token(test_email):
    token = create_email_token({"sub": test_email})
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token["sub"] == test_email
    assert "exp" in decoded_token
    assert "iat" in decoded_token
    assert datetime.utcfromtimestamp(decoded_token["exp"]) > datetime.utcnow()

@pytest.mark.asyncio
async def test_get_email_from_token(test_token, test_email):
    email = await get_email_from_token(test_token)
    assert email == test_email

@pytest.mark.asyncio
async def test_get_email_from_token_invalid_token():
    invalid_token = "invalid_token"
    with pytest.raises(HTTPException) as exc_info:
        await get_email_from_token(invalid_token)
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc_info.value.detail == "Invalid token for email verification"

@pytest.mark.asyncio
async def test_get_email_from_token_expired_token(test_email):
    # Create an expired token
    data = {"sub": test_email}
    expired_token = create_email_token(data)
    # Modify the token's exp to be in the past
    expired_token = jwt.encode({"sub": test_email, "exp": datetime.utcnow() - timedelta(seconds=1)}, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        await get_email_from_token(expired_token)
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc_info.value.detail == "Invalid token for email verification"










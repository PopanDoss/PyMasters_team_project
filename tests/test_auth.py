from jose import jwt
from fastapi import HTTPException, status
import pytest
from pymasters.repository.auth import (
    Hash, create_access_token, create_refresh_token,
    get_email_form_refresh_token, get_current_user, get_admin_user
)
from pymasters.settings import SECRET_KEY, ALGORITHM
from pymasters.database.models import User

# Tests for password hashing
def test_hash_password():
    password = "testpassword"
    hash = Hash()
    hashed_password = hash.get_password_hash(password)
    assert hash.verify_password(password, hashed_password)

def test_verify_password():
    password = "testpassword"
    wrong_password = "wrongpassword"
    hash = Hash()
    hashed_password = hash.get_password_hash(password)
    assert hash.verify_password(password, hashed_password)
    assert not hash.verify_password(wrong_password, hashed_password)

# Tests for token creation
def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_data["sub"] == "test@example.com"
    assert decoded_data["scope"] == "access_token"

def test_create_refresh_token():
    data = {"sub": "test@example.com"}
    token = create_refresh_token(data)
    decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_data["sub"] == "test@example.com"
    assert decoded_data["scope"] == "refresh_token"

# Test for extracting email from refresh token
def test_get_email_form_refresh_token():
    data = {"sub": "test@example.com"}
    refresh_token = create_refresh_token(data)
    email = get_email_form_refresh_token(refresh_token)
    assert email == "test@example.com"

    # Invalid scope
    access_token = create_access_token(data)
    with pytest.raises(HTTPException) as excinfo:
        get_email_form_refresh_token(access_token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == 'Invalid scope for token'

    # Invalid token
    with pytest.raises(HTTPException) as excinfo:
        get_email_form_refresh_token("invalid_token")
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == 'Could not validate credentials'

# Tests for checking user roles
@pytest.mark.asyncio
async def test_get_current_user(test_user, test_db):
    data = {"sub": test_user.email}
    token = create_access_token(data)
    fetched_user = await get_current_user(token, db=test_db)
    assert fetched_user.email == test_user.email

@pytest.mark.asyncio
async def test_get_admin_user(test_user, test_db):
    test_user.role = "admin"
    test_db.commit()
    data = {"sub": test_user.email}
    token = create_access_token(data)
    current_user = await get_admin_user(await get_current_user(token, db=test_db))
    assert current_user.email == test_user.email

    # Incorrect role
    test_user.role = "user"
    test_db.commit()
    with pytest.raises(HTTPException) as excinfo:
        await get_admin_user(await get_current_user(token, db=test_db))
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert excinfo.value.detail == "Operation not permitted"

















import pytest
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException

from pymasters.database.models import User
from pymasters.repository.users_repo import UserService, UsernameTaken, LoginFailed, InvalidRefreshtoken
from pymasters.schemas import UserModel
from pymasters.repository.auth import Hash

from jose import jwt, JWTError
from pymasters.services.auth_service import SECRET_KEY, ALGORITHM

hash_handler = Hash()

# Test for retrieving a user
def test_get_user(test_user, test_db: Session):
    user = UserService.get_user(username=test_user.email, db=test_db)
    assert user.email == test_user.email

# Test for checking if a username is available
def test_check_username_availability(test_user, test_db: Session):
    with pytest.raises(UsernameTaken):
        UserService.check_username_availablity(username=test_user.email, db=test_db)

# Test for creating a new user
def test_create_new_user(test_db: Session):
    new_user_data = UserModel(username="newuser@example.com", password="newpassword")
    new_user = UserService.creat_new_user(body=new_user_data, db=test_db)
    assert new_user.email == new_user_data.username

# Test for logging in a user
def test_login_user(test_user, test_db: Session):
    login_data = OAuth2PasswordRequestForm(username=test_user.email, password="testpassword", scope="")
    access_token, refresh_token = UserService.login_user(body=login_data, db=test_db)
    assert access_token is not None
    assert refresh_token is not None

# Test for logging in with an invalid password
def test_login_user_invalid_password(test_user, test_db: Session):
    login_data = OAuth2PasswordRequestForm(username=test_user.email, password="wrongpassword", scope="")
    with pytest.raises(LoginFailed):
        UserService.login_user(body=login_data, db=test_db)

# Test for refreshing an access token
def test_refresh_token(test_user, test_db: Session):
    login_data = OAuth2PasswordRequestForm(username=test_user.email, password="testpassword", scope="")
    _, refresh_token = UserService.login_user(body=login_data, db=test_db)
    new_access_token = UserService.refresh_token(refresh_token=refresh_token, db=test_db)
    assert new_access_token is not None

# Test for saving user information
def test_save_user(test_user, test_db: Session):
    test_user.email = "updated@example.com"
    updated_user = UserService.save_user(test_user, db=test_db)
    assert updated_user.email == "updated@example.com"

# Test for getting a user by email
def test_get_user_by_email(test_user, test_db: Session):
    user = UserService.get_user_by_email(email=test_user.email, db=test_db)
    assert user.email == test_user.email

# Test for confirming a user's email
def test_confirmed_email(test_user, test_db: Session):
    UserService.confirmed_email(email=test_user.email, db=test_db)
    confirmed_user = UserService.get_user_by_email(email=test_user.email, db=test_db)
    assert confirmed_user.confirmed is True

# Test for handling an invalid refresh token
def test_refresh_token_invalid(test_user, test_db: Session):
    # Create a valid token
    data = {"sub": test_user.email, "scope": "refresh_token"}
    correct_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    
    # Manually modify the token to make it invalid
    invalid_token = correct_token[:-1] + 'x'  # Change the last character
    
    with pytest.raises(HTTPException) as exc_info:
        UserService.refresh_token(refresh_token=invalid_token, db=test_db)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == 'Could not validate credentials'


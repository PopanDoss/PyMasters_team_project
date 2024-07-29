from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi_mail import FastMail, MessageSchema, MessageType

from sqlalchemy.orm import Session

from pymasters.services.auth_service import get_email_from_token

from typing import List

from datetime import date

from pymasters.schemas import UserModel, EmailSchema, RequestEmail, UserDisplayModel
from pymasters.database.db import get_db
from pymasters.database.models import User

from pymasters.repository.users_repo import UserService, UsernameTaken, LoginFailed
from pymasters.repository.auth import get_current_user, get_admin_user, get_moderator_user

from pymasters.services.email import send_email

from pymasters.settings import conf

router = APIRouter(prefix='/users', tags=['users'])

security = HTTPBearer()
user_servis = UserService()

@router.post("/signup")
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Create a new user account.

    Args:
        body (UserModel): The user information for account creation.
        background_tasks (BackgroundTasks): Background task manager for sending emails.
        request (Request): The current request context.
        db (Session): The database session.

    Returns:
        dict: A message indicating the success or failure of the signup process.

    Raises:
        HTTPException: If the username is already taken.
    """
    try:
        new_user = user_servis.creat_new_user(body, db)
        background_tasks.add_task(send_email, new_user.email, request.base_url)
    except UsernameTaken:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    return {"new_user": new_user.email, "detail": "User successfully created. Check your email for confirmation."}

@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    User login and token generation.

    Args:
        body (OAuth2PasswordRequestForm): The login form data (username and password).
        db (Session): The database session.

    Returns:
        dict: The access and refresh tokens.

    Raises:
        HTTPException: If the email is invalid or not confirmed, or if the credentials are incorrect.
    """
    user = user_servis.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")

    try:
        access_token, refresh_token = user_servis.login_user(body, db)
    except LoginFailed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Request email confirmation.

    Args:
        body (RequestEmail): The email address to confirm.
        background_tasks (BackgroundTasks): Background task manager for sending emails.
        request (Request): The current request context.
        db (Session): The database session.

    Returns:
        dict: A message indicating the status of the email confirmation request.
    """
    user = user_servis.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, request.base_url)
    return {"message": "Check your email for confirmation."}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm user email.

    Args:
        token (str): The email confirmation token.
        db (Session): The database session.

    Returns:
        dict: A message indicating the status of the email confirmation.

    Raises:
        HTTPException: If the verification fails.
    """
    email = await get_email_from_token(token)
    user = user_servis.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    user_servis.confirmed_email(email, db)
    return {"message": "Email confirmed"}

@router.post('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Refresh the access token.

    Args:
        credentials (HTTPAuthorizationCredentials): The refresh token.
        db (Session): The database session.

    Returns:
        dict: The new access and refresh tokens.
    """
    token = credentials.credentials
    access_token = user_servis.refresh_token(token, db)
    return {"access_token": access_token, "refresh_token": token, "token_type": "bearer"}

# Additional routes for role checks

@router.get('/admin')
async def admin_access(current_user: User = Depends(get_admin_user)):
    """
    Admin access route.

    Args:
        current_user (User): The currently authenticated admin user.

    Returns:
        dict: A message indicating access for admin users.
    """
    return {"message": "Welcome, admin!"}

@router.get('/moderator')
async def moderator_access(current_user: User = Depends(get_moderator_user)):
    """
    Moderator access route.

    Args:
        current_user (User): The currently authenticated moderator or admin user.

    Returns:
        dict: A message indicating access for moderators.
    """
    return {"message": "Welcome, moderator!"}

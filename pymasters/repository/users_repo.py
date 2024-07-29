from typing import Optional
from sqlalchemy.orm import Session

from fastapi import UploadFile, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from pymasters.database.models import User
from pymasters.repository.auth import create_access_token, create_refresh_token, Hash, get_email_form_refresh_token
from pymasters.schemas import UserModel

hash_handler = Hash()

class UsernameTaken(Exception):
    """Exception raised when a username is already taken."""
    pass

class LoginFailed(Exception):
    """Exception raised when login fails."""
    pass 

class InvalidRefreshtoken(Exception):
    """Exception raised when a refresh token is invalid."""
    pass


class UserService:
    """
    A service class to handle user-related operations.
    """

    @staticmethod
    def get_user(username: str, db: Session) -> Optional[User]:
        """
        Retrieves a user by username (email).

        Args:
            username (str): The username (email) of the user.
            db (Session): The database session.

        Returns:
            Optional[User]: The user if found, otherwise None.
        """
        return db.query(User).filter(User.email == username).first()

    @staticmethod
    def check_username_availablity(username: str, db: Session):
        """
        Checks if a username is available.

        Args:
            username (str): The username (email) to check.
            db (Session): The database session.

        Raises:
            UsernameTaken: If the username is already taken.
        """
        exist_user = UserService.get_user(username, db)
        if exist_user:
            raise UsernameTaken

    @staticmethod
    def creat_new_user(body: UserModel, db: Session) -> User:
        """
        Creates a new user.

        Args:
            body (UserModel): The user data.
            db (Session): The database session.

        Returns:
            User: The created user.
        """
        UserService.check_username_availablity(username=body.username, db=db)
        role = "admin" if db.query(User).count() == 0 else "user"
        new_user = User(email=body.username, password=hash_handler.get_password_hash(body.password), role=role)
        new_user = UserService.save_user(new_user, db)
        return new_user

    @staticmethod
    def login_user(body: OAuth2PasswordRequestForm, db: Session):
        """
        Logs in a user and generates access and refresh tokens.

        Args:
            body (OAuth2PasswordRequestForm): The login form data.
            db (Session): The database session.

        Returns:
            Tuple[str, str]: The access and refresh tokens.

        Raises:
            LoginFailed: If the login fails.
        """
        user = UserService.get_user(body.username, db)
        if user is None or not hash_handler.verify_password(body.password, user.password):
            raise LoginFailed

        data = {"sub": user.email}
        access_token = create_access_token(data=data)
        refresh_token = create_refresh_token(data=data)

        user.refresh_token = refresh_token
        UserService.save_user(user, db)
        return access_token, refresh_token

    @staticmethod
    def refresh_token(refresh_token: str, db: Session) -> str:
        """
        Refreshes an access token using a refresh token.

        Args:
            refresh_token (str): The refresh token.
            db (Session): The database session.

        Returns:
            str: The new access token.

        Raises:
            InvalidRefreshtoken: If the refresh token is invalid.
        """
        email = get_email_form_refresh_token(refresh_token)
        user = UserService.get_user(email, db)
        if user.refresh_token != refresh_token:
            user.refresh_token = None
            UserService.save_user(user, db)
            raise InvalidRefreshtoken

        access_token = create_access_token(data={"sub": email})
        return access_token

    @staticmethod
    def save_user(user_to_save: User, db: Session) -> User:
        """
        Saves a user to the database.

        Args:
            user_to_save (User): The user to save.
            db (Session): The database session.

        Returns:
            User: The saved user.
        """
        db.add(user_to_save)
        db.commit()
        db.refresh(user_to_save)
        return user_to_save

    @staticmethod
    def get_user_by_email(email: str, db: Session) -> Optional[User]:
        """
        Retrieves a user by email.

        Args:
            email (str): The email of the user.
            db (Session): The database session.

        Returns:
            Optional[User]: The user if found, otherwise None.
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def confirmed_email(email: str, db: Session) -> None:
        """
        Confirms a user's email.

        Args:
            email (str): The email to confirm.
            db (Session): The database session.
        """
        user = UserService.get_user_by_email(email, db)
        user.confirmed = True
        db.commit()

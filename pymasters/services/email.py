from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from pymasters.repository.users_repo import UserService
from pymasters.services.auth_service import create_email_token
from pymasters.settings import conf

async def send_email(email: EmailStr, host: str):
    """
    Sends a confirmation email to the specified email address with a verification token.

    Parameters:
    - email (EmailStr): The recipient's email address.
    - host (str): The base URL of the application, used in the email template.

    Returns:
    - None: The function does not return a value. If an error occurs, it is printed to the console.

    Raises:
    - ConnectionErrors: If there is a problem connecting to the email server or sending the email.
    """
    try:
        # Generate a verification token for the email address
        token_verification = create_email_token({"sub": email})

        # Create the email message schema
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "token": token_verification},
            subtype=MessageType.html
        )

        # Initialize FastMail with configuration settings
        fm = FastMail(conf)

        # Send the email using the specified template
        await fm.send_message(message, template_name="email_template.html")

    except ConnectionErrors as err:
        # Print the error if email sending fails
        print(f"Error sending email: {err}")


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Import the database URL from settings
from settings import SQLALCHEMY_DATABASE_URL

# Load environment variables from .env file
load_dotenv()

# Retrieve the database URL from the environment variable
SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')

# Create an engine object for interacting with the database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session factory for interacting with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get a database session
def get_db():
    """
    Creates a new database session and closes it after use.

    Used as a dependency in FastAPI to get a database session
    in requests.
    """
    try:
        # Create a new session
        db = SessionLocal()
        yield db
    finally:
        # Close the session after use
        db.close()

import pytest
from pydantic import ValidationError
from pymasters.schemas import (
    TransformationCreate, 
    PhotoCreate, 
    CommentCreate, 
    RequestEmail, 
    UserModel, 
    PhotoUpdate,
    PhotoDisplay,
    TransformationDisplay,
    CommentInDBBase
)
from fastapi import UploadFile
from datetime import datetime
from typing import List
import io


def test_transformation_create():
    # Test valid input
    data = {"transformation": "resize"}
    transformation = TransformationCreate(**data)
    assert transformation.transformation == "resize"

    # Test missing required field
    with pytest.raises(ValidationError):
        TransformationCreate()

def test_photo_create():
    # Test valid input
    file = io.BytesIO(b"fake image data")
    upload_file = UploadFile(filename="test.jpg", file=file)
    data = {"file": upload_file, "description": "Test photo", "tags": ["nature", "sky"]}
    photo = PhotoCreate(**data)
    assert photo.file == upload_file
    assert photo.description == "Test photo"
    assert photo.tags == ["nature", "sky"]

    # Test missing required field
    with pytest.raises(ValidationError):
        PhotoCreate(description="Test photo")

def test_photo_update():
    # Test valid input
    data = {"description": "Updated description"}
    photo_update = PhotoUpdate(**data)
    assert photo_update.description == "Updated description"

    # Test empty input
    data = {}
    photo_update = PhotoUpdate(**data)
    assert photo_update.description is None

def test_comment_create():
    # Test valid input
    data = {"content": "This is a comment"}
    comment = CommentCreate(**data)
    assert comment.content == "This is a comment"

    # Test missing required field
    with pytest.raises(ValidationError):
        CommentCreate()

def test_request_email():
    # Test valid input
    data = {"email": "test@example.com"}
    email = RequestEmail(**data)
    assert email.email == "test@example.com"

    # Test invalid email
    with pytest.raises(ValidationError):
        RequestEmail(email="invalid-email")

def test_user_model():
    # Test valid input
    data = {"username": "testuser", "password": "password"}
    user = UserModel(**data)
    assert user.username == "testuser"
    assert user.password == "password"

    # Test missing required field
    with pytest.raises(ValidationError):
        UserModel(username="testuser")


def test_photo_display():
    # Test valid input
    data = {
        "id": 1,
        "photo_urls": "http://example.com/photo.jpg",
        "description": "A photo",
        "tags": ["tag1", "tag2"],
        "transformations": []
    }
    photo_display = PhotoDisplay(**data)
    assert photo_display.id == 1
    assert photo_display.photo_urls == "http://example.com/photo.jpg"
    assert photo_display.description == "A photo"
    assert photo_display.tags == ["tag1", "tag2"]

    # Test missing required field (id)
    data = {
        "photo_urls": "http://example.com/photo.jpg",
        "description": "A photo",
        "tags": ["tag1", "tag2"],
        "transformations": []
    }
    with pytest.raises(ValidationError):
        PhotoDisplay(**data)

def test_transformation_display():
    # Test valid input
    data = {
        "id": 1,
        "transformation_url": "http://example.com/transform.jpg",
        "qr_code_url": "http://example.com/qr_code.jpg",
        "created_at": datetime.now()
    }
    transformation_display = TransformationDisplay(**data)
    assert transformation_display.id == 1
    assert transformation_display.transformation_url == "http://example.com/transform.jpg"
    assert transformation_display.qr_code_url == "http://example.com/qr_code.jpg"

    # Test missing required field
    with pytest.raises(ValidationError):
        TransformationDisplay(id=1, transformation_url="http://example.com/transform.jpg", created_at=datetime.now())

def test_comment_in_db_base():
    # Test valid input
    data = {
        "user_id": 1,
        "photo_id": 1,
        "content": "Nice photo!",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    comment_in_db = CommentInDBBase(**data)
    assert comment_in_db.user_id == 1
    assert comment_in_db.photo_id == 1
    assert comment_in_db.content == "Nice photo!"

    # Test missing required field
    with pytest.raises(ValidationError):
        CommentInDBBase(user_id=1, photo_id=1, created_at=datetime.now(), updated_at=datetime.now())



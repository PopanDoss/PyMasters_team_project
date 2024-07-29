import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pymasters.database.models import User, Photos, Tags, Comment, Transformation

def test_create_user(test_db: Session):
    user = User(email="newuser@example.com", password="hashedpassword")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    assert user.id is not None
    assert user.email == "newuser@example.com"

def test_create_photo(test_db: Session, test_user: User):
    photo = Photos(photo_urls="http://example.com/photo.jpg", created_by_id=test_user.id)
    test_db.add(photo)
    test_db.commit()
    test_db.refresh(photo)
    
    assert photo.id is not None
    assert photo.created_by_id == test_user.id

def test_create_tag(test_db: Session):
    tag = Tags(tag="Nature")
    test_db.add(tag)
    test_db.commit()
    test_db.refresh(tag)
    
    assert tag.id is not None
    assert tag.tag == "Nature"

def test_create_comment(test_db: Session, test_user: User):
    photo = Photos(photo_urls="http://example.com/photo.jpg", created_by_id=test_user.id)
    test_db.add(photo)
    test_db.commit()
    test_db.refresh(photo)
    
    comment = Comment(content="Nice photo!", user_id=test_user.id, photo_id=photo.id)
    test_db.add(comment)
    test_db.commit()
    test_db.refresh(comment)
    
    assert comment.id is not None
    assert comment.content == "Nice photo!"
    assert comment.user_id == test_user.id
    assert comment.photo_id == photo.id

def test_create_transformation(test_db: Session):
    # Створення нового фото
    photo = Photos(photo_urls="http://example.com/photo.jpg", created_by_id=1)
    test_db.add(photo)
    test_db.commit()  # Збереження фото для отримання photo.id

    # Створення нової трансформації
    transformation = Transformation(
        photo_id=photo.id,
        transformation_url="http://example.com/transformed.jpg",
        qr_code_url="http://example.com/qr_code.jpg"
    )
    test_db.add(transformation)
    test_db.commit()

    # Перевірка чи трансформація була створена
    assert transformation.id is not None
    assert transformation.photo_id == photo.id
    assert transformation.transformation_url == "http://example.com/transformed.jpg"
    assert transformation.qr_code_url == "http://example.com/qr_code.jpg"



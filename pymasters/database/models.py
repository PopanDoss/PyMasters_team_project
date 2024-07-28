from sqlalchemy import Column, Integer, String, Boolean, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(String(50), default="user")  # Added role field

class Photos(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True)
    photo_urls = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True) # Added description field
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")
    tags = relationship("Tags", secondary="photo_tags", back_populates="photos") # Added relation with tags
    comments = relationship("Comment", back_populates="photo")
    transformations = relationship("Transformation", back_populates="photo")  # Added transformations relationship

class Tags(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    tag = Column(String(255), nullable=False, unique=True)  # Tags are unique
    photos = relationship("Photos", secondary="photo_tags", back_populates="tags") # Added back_populates for reverse relationship

photo_tags = Table(
    'photo_tags',
    Base.metadata,
    Column('photo_id', ForeignKey('photos.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    photo_id = Column(Integer, ForeignKey('photos.id'))
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())

    photo = relationship("Photos", back_populates="comments")
    user = relationship("User")

class Transformation(Base):
    __tablename__ = "transformations"
    id = Column(Integer, primary_key=True)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False)
    transformation_url = Column(String(255), nullable=False)
    qr_code_url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())

    photo = relationship("Photos", back_populates="transformations")

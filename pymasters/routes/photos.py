from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from pymasters.services.cloudinary_service import upload_photo_to_cloudinary, delete_photo_from_cloudinary

from pymasters.database.db import get_db
from pymasters.database.models import User, Photos, Tags
from pymasters.repository.auth import get_current_user
from pymasters.schemas import PhotoBase, PhotoCreate, PhotoUpdate, PhotoDisplay

router = APIRouter(prefix="/photos", tags=["photos"])

@router.post("/upload", response_model=PhotoDisplay)
async def upload_photo(file: UploadFile = File(...), description: str = "", tags: List[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Завантаження світлини з описом та тегами
    """
    # Завантаження фото до Cloudinary
    photo_url = upload_photo_to_cloudinary(file)
    # Створення нової світлини у БД
    new_photo = Photos(photo_urls=photo_url, description=description, created_by_id=current_user.id)
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)

    # Додавання тегів
    if tags:
        for tag_name in tags:
            tag = db.query(Tags).filter(Tags.tag == tag_name).first()
            if not tag:
                tag = Tags(tag=tag_name)
                db.add(tag)
            new_photo.tags.append(tag)
        db.commit()
        db.refresh(new_photo) 

    
    tag_names = [tag.tag for tag in new_photo.tags]

    add_photo = PhotoDisplay(
        id=new_photo.id,
        photo_urls=new_photo.photo_urls,
        description=new_photo.description,
        tags=tag_names
    )

    return add_photo

@router.delete("/{photo_id}")
async def delete_photo(photo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Видалення світлини
    """
    photo = db.query(Photos).filter(Photos.id == photo_id, Photos.created_by_id == current_user.id).first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    # Видалення фото з Cloudinary
    delete_photo_from_cloudinary(photo.photo_urls)
    db.delete(photo)
    db.commit()
    return {"detail": "Photo deleted"}

@router.put("/{photo_id}")
async def update_photo(photo_id: int, description: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Редагування опису світлини
    """
    photo = db.query(Photos).filter(Photos.id == photo_id, Photos.created_by_id == current_user.id).first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    photo.description = description
    db.commit()
    return {"detail": "Photo updated"}

@router.get("/{photo_id}", response_model=PhotoDisplay)
async def get_photo(photo_id: int, db: Session = Depends(get_db)):
    """
    Отримання світлини за унікальним посиланням
    """
    photo = db.query(Photos).filter(Photos.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    
    tag_names = [tag.tag for tag in photo.tags]

    photo_display = PhotoDisplay(
        id=photo.id,
        photo_urls=photo.photo_urls,
        description=photo.description,
        tags=tag_names
        )
    
    return photo_display


from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import logging

from pymasters.services.cloudinary_service import upload_photo_to_cloudinary, delete_photo_from_cloudinary, transform_photo

from pymasters.database.db import get_db
from pymasters.database.models import User, Photos, Tags, Transformation
from pymasters.repository.auth import get_current_user, get_admin_user
from pymasters.schemas import PhotoBase, PhotoCreate, PhotoUpdate, PhotoDisplay, TransformationDisplay

router = APIRouter(prefix="/photos", tags=["photos"])

logger = logging.getLogger(__name__)

@router.post("/upload", response_model=PhotoDisplay)
async def upload_photo(
    file: UploadFile = File(...),
    description: str = Form(...),
    tags: List[str] = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a photo with description and tags.

    Args:
        file (UploadFile): The photo file to upload.
        description (str): The description of the photo.
        tags (List[str]): The tags associated with the photo.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        PhotoDisplay: The uploaded photo details.
    """
    tags = tags or []

    # Upload the photo to Cloudinary
    photo_url = upload_photo_to_cloudinary(file.file)
    
    # Create a new photo record in the database
    new_photo = Photos(
        photo_urls=photo_url,
        description=description,
        created_by_id=current_user.id
    )
    
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    
    # Add tags
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

    return PhotoDisplay(
        id=new_photo.id,
        photo_urls=new_photo.photo_urls,
        description=new_photo.description,
        tags=tag_names
    )

@router.post("/transform", response_model=TransformationDisplay)
async def transform_photo_endpoint(
    photo_id: int,
    transformation: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Apply transformation to photo and generate QR code.

    Args:
        photo_id (int): The ID of the photo to transform.
        transformation (str): The transformation to apply.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        TransformationDisplay: The transformed photo details.

    Raises:
        HTTPException: If the photo is not found or transformation fails.
    """
    logger.info(f"Requested transformation: {transformation}")
    
    photo = db.query(Photos).filter(Photos.id == photo_id, Photos.created_by_id == current_user.id).first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    
    result = transform_photo(photo.photo_urls, transformation)
    
    logger.info(f"Transformation result: {result}")
    
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    
    # Create a new record in the database
    try:
        new_transformation = Transformation(
            photo_id=photo.id,
            transformation_url=result["transformation_url"],
            qr_code_url=result["qr_code_url"]
        )
        db.add(new_transformation)
        db.commit()
        db.refresh(new_transformation)
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

    return TransformationDisplay(
        id=new_transformation.id,
        photo_id=new_transformation.photo_id,
        transformation_url=new_transformation.transformation_url,
        qr_code_url=new_transformation.qr_code_url,
        created_at=new_transformation.created_at
    )

@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a photo.

    Args:
        photo_id (int): The ID of the photo to delete.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        dict: A message indicating successful deletion.

    Raises:
        HTTPException: If the photo is not found or the user is not authorized to delete the photo.
    """
    photo = db.query(Photos).filter(Photos.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    if photo.created_by_id != current_user.id:
        admin_user = await get_admin_user(current_user)
        if not admin_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")

    delete_photo_from_cloudinary(photo.photo_urls)
    db.delete(photo)
    db.commit()
    
    return {"detail": "Photo deleted"}

@router.put("/{photo_id}")
async def update_photo(
    photo_id: int,
    description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update photo description.

    Args:
        photo_id (int): The ID of the photo to update.
        description (str): The new description for the photo.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        dict: A message indicating successful update.

    Raises:
        HTTPException: If the photo is not found or the user is not authorized to update the photo.
    """
    photo = db.query(Photos).filter(Photos.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    if photo.created_by_id != current_user.id:
        admin_user = await get_admin_user(current_user)
        if not admin_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")
    
    photo.description = description
    db.commit()
    
    return {"detail": "Photo updated"}

@router.get("/{photo_id}", response_model=PhotoDisplay)
async def get_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a photo by unique ID.

    Args:
        photo_id (int): The ID of the photo to retrieve.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        PhotoDisplay: The retrieved photo details.

    Raises:
        HTTPException: If the photo is not found or the user is not authorized to view the photo.
    """
    photo = db.query(Photos).filter(Photos.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    if photo.created_by_id != current_user.id:
        admin_user = await get_admin_user(current_user)
        if not admin_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")

    tag_names = [tag.tag for tag in photo.tags]

    return PhotoDisplay(
        id=photo.id,
        photo_urls=photo.photo_urls,
        description=photo.description,
        tags=tag_names
    )

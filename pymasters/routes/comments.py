from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from pymasters.schemas import CommentCreate, Comment, CommentUpdate
from pymasters.database.models import User, Photos
from pymasters.database.models import Comment as table_Comment
from pymasters.database.db import get_db
from pymasters.repository.auth import get_current_user

router = APIRouter(prefix='/comments', tags=['comments'])


@router.post("/photos/{photo_id}/comments/", response_model=Comment)
def create_comment(photo_id: int, comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Creates a new comment for a specific photo.

    Args:
        photo_id (int): The ID of the photo to comment on.
        comment (CommentCreate): The comment data.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        Comment: The created comment.

    Raises:
        HTTPException: If the photo is not found.
    """
    photo = db.query(Photos).filter(Photos.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    db_comment = table_Comment(content=comment.content, photo_id=photo_id, user_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.put("/comments/{comment_id}/", response_model=Comment)
def update_comment(comment_id: int, comment: CommentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Updates an existing comment.

    Args:
        comment_id (int): The ID of the comment to update.
        comment (CommentUpdate): The updated comment data.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        Comment: The updated comment.

    Raises:
        HTTPException: If the comment is not found or the user is not authorized to update the comment.
    """
    db_comment = db.query(table_Comment).filter(table_Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    
    for key, value in comment.dict().items():
        setattr(db_comment, key, value)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment


@router.delete("/comments/{comment_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Deletes an existing comment.

    Args:
        comment_id (int): The ID of the comment to delete.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Raises:
        HTTPException: If the comment is not found or the user is not authorized to delete the comment.
    """
    db_comment = db.query(table_Comment).filter(table_Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if current_user.role not in ['admin', 'moderator']:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    db.delete(db_comment)
    db.commit()
    return None

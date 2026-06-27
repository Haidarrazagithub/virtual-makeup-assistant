from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.look import SavedLook
from app.schemas.look import SavedLookResponse, SavedLookCreate

router = APIRouter()


@router.post("", response_model=SavedLookResponse)
def save_look(look_in: SavedLookCreate, db: Session = Depends(get_db)):
    """
    Saves a customized makeup configuration.
    """
    # Check if a look with the same name already exists
    existing = db.query(SavedLook).filter(SavedLook.name == look_in.name).first()
    if existing:
        # Update existing look
        for key, value in look_in.dict().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing

    db_look = SavedLook(**look_in.dict())
    db.add(db_look)
    db.commit()
    db.refresh(db_look)
    return db_look


@router.get("", response_model=List[SavedLookResponse])
def list_saved_looks(db: Session = Depends(get_db)):
    """
    Retrieves all bookmarked makeup configurations.
    """
    return db.query(SavedLook).order_by(SavedLook.created_at.desc()).all()


@router.delete("/{look_id}")
def delete_saved_look(look_id: int, db: Session = Depends(get_db)):
    """
    Deletes a specific bookmarked configuration.
    """
    look = db.query(SavedLook).filter(SavedLook.id == look_id).first()
    if not look:
        raise HTTPException(
            status_code=404,
            detail="Saved look not found."
        )
    db.delete(look)
    db.commit()
    return {"message": "Saved look successfully deleted."}

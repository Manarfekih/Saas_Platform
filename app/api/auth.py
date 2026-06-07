from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.services.auth_service import (
    create_user,
    authenticate_user,
    generate_token
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    return create_user(db, user.name, user.email, user.password)


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = authenticate_user(db, user.email, user.password)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = generate_token(db_user)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

from app.core.deps import get_current_user

@router.get("/me")
def me(current_user=Depends(get_current_user)):

    return {
        "id": current_user.id,
        "email": current_user.email
    }
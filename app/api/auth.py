from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi import UploadFile, File
import uuid
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, UserUpdate
from app.services.auth_service import (
    create_user,
    authenticate_user,
    generate_token
)
from app.core.security import hash_password, verify_password
from app.core.deps import get_current_user

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


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    profile_image = current_user.profile_image
    if profile_image and not profile_image.startswith("/"):
        profile_image = f"/{profile_image}"

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "profile_image": profile_image
    }


@router.post("/me/profile-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image."
        )

    upload_dir = Path("uploads") / "profiles"
    upload_dir.mkdir(parents=True, exist_ok=True)

    allowed_extensions = {"png", "jpg", "jpeg", "webp"}

    extension = Path(file.filename or "").suffix.lower().lstrip(".")

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format."
        )

    contents = await file.read()

    max_size = 5 * 1024 * 1024

    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail="Image too large."
        )

    if current_user.profile_image:
        old_image = Path(current_user.profile_image.lstrip("/"))
        if old_image.exists():
            old_image.unlink()

    filename = f"{uuid.uuid4()}.{extension}"
    file_path = upload_dir / filename

    file_path.write_bytes(contents)

    current_user.profile_image = f"/{file_path.as_posix()}"

    db.commit()
    db.refresh(current_user)

    return {
        "profile_image": current_user.profile_image
    }


@router.put("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # If the user wants to change their password, verify current first
    if payload.new_password:
        if not payload.current_password:
            raise HTTPException(
                status_code=400,
                detail="Current password is required to set a new password"
            )
        if not verify_password(payload.current_password, current_user.password):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect"
            )
        current_user.password = hash_password(payload.new_password)

    if payload.name is not None:
        current_user.name = payload.name

    if payload.email is not None and payload.email != current_user.email:
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = payload.email

    db.commit()
    db.refresh(current_user)
    return current_user

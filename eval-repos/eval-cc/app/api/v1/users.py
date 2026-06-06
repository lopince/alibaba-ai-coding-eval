from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models.database import User, get_db
from app.schemas.schemas import UserCreateSchema, UserResponseSchema, UserUpdateSchema
from app.auth.decorators import require_auth
import hashlib

router = APIRouter(prefix="/users", tags=["users"])


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@router.get("/")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_active == True).all()
    schema = UserResponseSchema(many=True)
    return schema.dump(users)


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    schema = UserResponseSchema()
    return schema.dump(user)


@router.post("/", status_code=201)
def create_user(body: dict, db: Session = Depends(get_db)):
    schema = UserCreateSchema()
    data = schema.load(body)

    if db.query(User).filter(User.username == data["username"]).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    if db.query(User).filter(User.email == data["email"]).first():
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        username=data["username"],
        email=data["email"],
        full_name=data.get("full_name"),
        password_hash=_hash_password(data["password"]),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    response_schema = UserResponseSchema()
    return response_schema.dump(user)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()


@router.put("/{user_id}")
@require_auth
def update_user(user_id: int, body: dict, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    schema = UserUpdateSchema()
    data = schema.load(body)

    existing = db.query(User).filter(User.email == data["email"], User.id != user_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already in use")

    user.email = data["email"]
    db.commit()
    db.refresh(user)

    response_schema = UserResponseSchema()
    return response_schema.dump(user)

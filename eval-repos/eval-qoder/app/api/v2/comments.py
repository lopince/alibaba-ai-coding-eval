from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models.database import Comment, get_db
from app.schemas.schemas import CommentCreateSchema, CommentResponseSchema

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/")
def list_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    schema = CommentResponseSchema(many=True)
    return schema.dump(comments)


@router.post("/", status_code=201)
def create_comment(body: dict, request: Request, db: Session = Depends(get_db)):
    schema = CommentCreateSchema()
    data = schema.load(body)

    comment = Comment(
        post_id=data["post_id"],
        author_id=request.state.user_id,
        content=data["content"],
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    response_schema = CommentResponseSchema()
    return response_schema.dump(comment)

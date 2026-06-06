from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models.database import Post, get_db
from app.schemas.schemas import PostCreateSchema, PostResponseSchema

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/")
def list_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    schema = PostResponseSchema(many=True)
    return schema.dump(posts)


@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    schema = PostResponseSchema()
    return schema.dump(post)


@router.post("/", status_code=201)
def create_post(body: dict, request: Request, db: Session = Depends(get_db)):
    schema = PostCreateSchema()
    data = schema.load(body)

    post = Post(
        title=data["title"],
        body=data.get("body"),
        author_id=request.state.user_id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    response_schema = PostResponseSchema()
    return response_schema.dump(post)

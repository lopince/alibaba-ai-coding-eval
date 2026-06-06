from fastapi import FastAPI
from app.api.v1 import users, posts
from app.api.v2 import comments
from app.auth.middleware import AuthMiddleware

app = FastAPI(title="User Management API", version="1.0.0")

app.add_middleware(AuthMiddleware)

app.include_router(users.router, prefix="/v1")
app.include_router(posts.router, prefix="/v1")
app.include_router(comments.router, prefix="/v2")


@app.get("/health")
def health():
    return {"status": "ok"}

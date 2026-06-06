import functools

from fastapi import HTTPException, Request
from jose import JWTError, jwt

from app.auth.middleware import ALGORITHM, SECRET_KEY


def require_auth(func):
    @functools.wraps(func)
    def wrapper(request: Request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user_id = payload["sub"]
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        return func(request, *args, **kwargs)

    return wrapper

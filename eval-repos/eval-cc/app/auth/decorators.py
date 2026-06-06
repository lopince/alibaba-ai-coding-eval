import asyncio
from functools import wraps
from fastapi import Request, HTTPException
from jose import jwt, JWTError
from app.auth.middleware import SECRET_KEY, ALGORITHM


def require_auth(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        if not request:
            raise HTTPException(status_code=500, detail="Request not available")

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user_id = payload["sub"]
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper

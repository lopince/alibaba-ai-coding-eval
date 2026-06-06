# User Management API

A REST API for managing users and posts, built with FastAPI.

## Running

```bash
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /v1/users | List all users |
| GET | /v1/users/{id} | Get a user |
| POST | /v1/users | Create a user |
| DELETE | /v1/users/{id} | Delete a user |
| GET | /v1/posts | List all posts |
| GET | /v1/posts/{id} | Get a post |
| POST | /v1/posts | Create a post |
| GET | /health | Health check |

## Testing

```bash
python -m unittest discover tests/
```

## Auth

All endpoints except `/health` and `/docs` require a Bearer token in the Authorization header.

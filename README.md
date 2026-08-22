# Story Platform API

A RESTful backend for a story publishing platform built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy 2.0**.

> **Current status:** authentication and user management are implemented. Story endpoints are scaffolded and still in development.

## Tech Stack

- Python 3.13+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0 (async)
- asyncpg
- Alembic
- Pydantic Settings
- JWT authentication
- Passlib / bcrypt
- uv

## Features

### Implemented

- JWT-based authentication
- User registration and login
- Authenticated user profile
- User profile updates
- Password changes
- Role-based authorization
- User account soft deletion
- Permanent user account deletion
- Custom application exceptions
- Centralized global exception handling
- Standardized API error responses
- Centralized database transaction rollback
- Async PostgreSQL access
- Alembic database migrations
- Versioned API routes (`/api/v1`)
- Health check endpoint
- OpenAPI / Swagger documentation

### In Progress

- Story CRUD
- Draft and publishing workflow
- Story search
- Pagination

## Project Structure

```text
story-platform-api/
├── alembic/               # Database migrations
├── app/
│   ├── api/
│   │   ├── deps.py        # Shared API dependencies
│   │   └── v1/            # Version 1 endpoints
│   ├── core/              # Configuration, security, logging, and exceptions
│   ├── crud/              # Database access layer
│   ├── db/                # SQLAlchemy base, async session, and transaction handling
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic request, response, and common API schemas
│   ├── services/          # Business logic
│   ├── utils/             # Shared utilities
│   └── main.py            # Application entry point
├── tests/
├── alembic.ini
├── pyproject.toml
└── uv.lock
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/nouvalkaff/story-platform-api.git
cd story-platform-api
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/story_platform
SECRET_KEY=replace-with-a-secure-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 4. Run database migrations

```bash
uv run alembic upgrade head
```

### 5. Start the development server

```bash
uv run fastapi dev app/main.py
```

API: `http://127.0.0.1:8000`

Docs: `http://127.0.0.1:8000/docs`

## API

Base path: `/api/v1`

| Method   | Endpoint                                  | Description                              |
| -------- | ----------------------------------------- | ---------------------------------------- |
| `POST`   | `/api/v1/auth/login`                      | Authenticate and receive an access token |
| `POST`   | `/api/v1/users/create`                    | Create a user                            |
| `GET`    | `/api/v1/users/me`                        | Get the authenticated user               |
| `PATCH`  | `/api/v1/users/{user_id}`                 | Update user details                      |
| `PATCH`  | `/api/v1/users/change-password/{user_id}` | Change a user's password                 |
| `DELETE` | `/api/v1/users/sdelete/{user_id}`         | Deactivate a user account                |
| `DELETE` | `/api/v1/users/hdelete/{user_id}`         | Permanently delete a user account        |
| `GET`    | `/health`                                 | Application health check                 |

## Error Handling

The application uses centralized exception handling to keep API error responses consistent and avoid repetitive `try/except` blocks across endpoints.

Handled exceptions include:

- Application-specific exceptions
- FastAPI / Starlette HTTP exceptions
- Request validation errors
- Pydantic validation errors
- Database integrity errors
- SQLAlchemy errors
- Unexpected application errors

Error responses follow a consistent structure:

```json
{
  "status_code": 400,
  "status": false,
  "message": "Bad request",
  "data": null
}
```

Internal exception details are not exposed to clients. Application-specific exceptions are separated from the API layer, allowing services to raise domain-related errors without directly depending on `HTTPException`.

## Database Transaction Handling

Database sessions use SQLAlchemy's asynchronous `AsyncSession`.

Transaction rollback is handled centrally through the database session dependency, allowing CRUD and service functions to propagate database exceptions without repeating rollback logic in every operation.

```text
Request
   ↓
Router
   ↓
Service
   ↓
CRUD
   ↓
Database
   ↓
Exception
   ↓
Session Rollback
   ↓
Global Exception Handler
   ↓
Standardized API Response
```

## API Documentation

The API collection is available on Postman:

[View Story Platform API on Postman](https://www.postman.com/nouvalkaffs-team/workspace/story-platform-api/collection/23758510-b4101b6e-113b-4952-9a04-be148b92f795?action=share&source=copy-link&creator=23758510)

You can also use the built-in Swagger UI while the application is running:

```text
http://127.0.0.1:8000/docs
```

## Authentication

Protected endpoints use Bearer token authentication:

```http
Authorization: Bearer <access_token>
```

Obtain a token from:

```text
POST /api/v1/auth/login
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

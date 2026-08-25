# Story Platform API

Story Platform API is an asynchronous REST API for user accounts and short stories. It provides JWT authentication, role-based access control, user lifecycle management, and authenticated story creation.

## Tech Stack

- Python 3.13+
- FastAPI
- PostgreSQL with SQLAlchemy 2.0 and asyncpg
- Alembic migrations
- Pydantic Settings
- JWT with python-jose
- Passlib and bcrypt for password hashing
- uv for dependency management

## Prerequisites

- Python 3.13 or newer
- PostgreSQL
- [uv](https://docs.astral.sh/uv/)

## Installation

```bash
git clone https://github.com/nouvalkaff/story-platform-api.git
cd story-platform-api
uv sync
```

## Configuration

Create a `.env` file in the project root.

```env
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/story_platform
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

`ENVIRONMENT` and `SECRET_KEY` are required. `ENVIRONMENT` accepts `development` or `production`; SQL query logging is enabled only in development. `DATABASE_URL`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES` have defaults, but setting them explicitly is recommended.

## Run Locally

Apply the database schema:

```bash
uv run alembic upgrade head
```

Start the development server:

```bash
uv run fastapi dev app/main.py
```

The API is available at `http://127.0.0.1:8000`, with interactive documentation at `http://127.0.0.1:8000/docs`.

## Postman Collection

[View the Story Platform API collection](https://www.postman.com/nouvalkaffs-team/workspace/story-platform-api/collection/23758510-b4101b6e-113b-4952-9a04-be148b92f795?action=share&source=copy-link&creator=23758510)

## Authentication

Log in through `POST /api/v1/auth/login` to receive a JWT access token. Send the token to protected endpoints with:

```http
Authorization: Bearer <access_token>
```

## API Endpoints

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/` | Public | API welcome response |
| `GET` | `/health` | Public | Health check |
| `POST` | `/api/v1/auth/login` | Public | Authenticate and receive an access token |
| `POST` | `/api/v1/users/create` | Public or admin | Create a user; authenticated creation requires an admin token |
| `GET` | `/api/v1/users/me` | Authenticated | Get the current user profile |
| `GET` | `/api/v1/users/all` | Admin | List users, with active/inactive filters |
| `PATCH` | `/api/v1/users/{user_id}` | Owner or admin | Update a user's email or full name |
| `PATCH` | `/api/v1/users/change-password/{user_id}` | Owner or admin | Change a user password |
| `DELETE` | `/api/v1/users/sdelete/{user_id}` | Owner or admin | Deactivate a user account |
| `DELETE` | `/api/v1/users/hdelete/{user_id}` | Owner or admin | Permanently delete a user and their stories; use `is_agree=true` when the user owns stories |
| `POST` | `/api/v1/your-story/add` | Authenticated | Create a story for the current user |

## Project Structure

```text
app/
|-- api/          # Route definitions and authentication dependencies
|-- core/         # Configuration, security, logging, and exception handlers
|-- crud/         # Database access operations
|-- db/           # SQLAlchemy session and declarative base
|-- models/       # User and story ORM models
|-- schemas/      # Request and response models
|-- services/     # Authentication and story business logic
`-- main.py       # FastAPI application entry point
alembic/           # Database migrations
```

## License

This project is licensed under the [MIT License](LICENSE).

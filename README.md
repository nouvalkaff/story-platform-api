# Story Platform API

Asynchronous REST API for user accounts and short stories. The service is built with FastAPI, uses PostgreSQL through SQLAlchemy 2.0, and protects authenticated resources with JWT bearer tokens.

## Features

- JWT authentication with active-user and token consistency checks.
- User registration, profile updates, password changes, and account deletion.
- Admin-only user listing and administrative account operations.
- Story creation with `DRAFT` and `PUBLISHED` statuses.
- Authenticated story detail and per-user story listing endpoints.
- Authenticated published-story listing with pagination and optional title search.
- Consistent response envelopes for user and story endpoints.
- Alembic migrations, including the migration from `is_published` to `status`.

## Technology

- Python 3.13+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0 with `asyncpg`
- Pydantic V2 and pydantic-settings
- Alembic
- JWT via `python-jose`
- Password hashing via Passlib and bcrypt
- `uv` for dependency management

## Requirements

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

Create a `.env` file in the project root:

```env
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/story_platform
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

`ENVIRONMENT` is required and must be `development` or `production`. `SECRET_KEY` is required. `DATABASE_URL` defaults to the PostgreSQL URL shown above; `ALGORITHM` defaults to `HS256`; and `ACCESS_TOKEN_EXPIRE_MINUTES` defaults to `60`.

SQLAlchemy query logging is enabled automatically in the `development` environment.

## Database and local run

Apply all migrations before starting the API:

```bash
uv run alembic upgrade head
```

Start the development server:

```bash
uv run fastapi dev app/main.py
```

The API is available at `http://127.0.0.1:8000`.

- OpenAPI UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `GET /health`

## Authentication

Log in with:

```http
POST /api/v1/auth/login
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

The response contains an access token. Send it to protected endpoints using:

```http
Authorization: Bearer <access_token>
```

The API validates the JWT and, where the endpoint loads the current user, verifies that the account still exists and is active.

## Response format

User and story endpoints return this envelope:

```json
{
  "status_code": 200,
  "status": true,
  "message": "Success",
  "data": {}
}
```

The login endpoint returns the token fields directly (`access_token` and `token_type`) together with `status_code` and `status`.

## API endpoints

The versioned API prefix is `/api/v1`.

### System and authentication

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `GET` | `/` | Public | API welcome response |
| `GET` | `/health` | Public | Health check |
| `POST` | `/api/v1/auth/login` | Public | Authenticate and issue a JWT access token |

### Users

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `POST` | `/api/v1/users/create` | Public or admin-authenticated | Create a user; an optional bearer token must belong to an admin |
| `GET` | `/api/v1/users/me` | Authenticated | Return the current user's profile |
| `GET` | `/api/v1/users/all` | Admin | List active and/or inactive users using `include_active` and `include_inactive` |
| `PATCH` | `/api/v1/users/{user_id}` | Owner or admin | Update email and full name |
| `PATCH` | `/api/v1/users/change-password/{user_id}` | Owner or admin | Change a user's password |
| `DELETE` | `/api/v1/users/sdelete/{user_id}` | Owner or admin | Deactivate a user account |
| `DELETE` | `/api/v1/users/hdelete/{user_id}` | Owner or admin | Permanently delete a user; use `is_agree=true` when the user owns stories |

### Stories

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| `POST` | `/api/v1/story/add` | Authenticated | Create a story for the current user; new stories default to `draft` |
| `GET` | `/api/v1/story/{story_id}` | Authenticated | Get a story; drafts are available to their author, while other users can only view published stories |
| `GET` | `/api/v1/story/user/{user_id}` | Authenticated | List a user's stories with `page` and `page_limit`; authors can see drafts, other users see published stories only |
| `GET` | `/api/v1/story/published` | Authenticated | List published stories with pagination and optional title search |

#### Published stories

Request parameters:

| Parameter | Default | Description |
| --- | --- | --- |
| `page` | `1` | Page number; must be at least `1` |
| `size` | `5` | Number of stories per page; must be at least `1` |
| `q` | omitted | Optional case-insensitive search term matched against the story title |

An omitted, empty, or whitespace-only `q` returns all published stories without a search filter.

Example:

```bash
curl --location "http://127.0.0.1:8000/api/v1/story/published?page=1&size=5&q=mystery" \
  --header "Authorization: Bearer <access_token>"
```

The response data contains `total`, `page`, `size`, and `stories`.

## Story status

Stories use the `StoryStatus` enum:

```text
draft
published
```

Publishing sets `status` to `published` and records `published_at`. Returning a story to draft sets `status` to `draft` and clears `published_at`.

## Database migrations

Migration files are stored in `alembic/versions`. The migration `1407aa9efb66_replace_is_published_with_story_status.py` converts legacy boolean values as follows:

- `is_published = false` → `status = draft`
- `is_published = true` → `status = published`

Run `uv run alembic upgrade head` after configuring the database.

## Tests

Run the test suite with the standard library test runner:

```bash
uv run python -m unittest discover -s tests -p "test_*.py"
```

## Project structure

```text
app/
├── api/          # FastAPI routers and authentication dependencies
├── core/         # Settings, security, logging, and exception handling
├── crud/         # Database queries and persistence operations
├── db/           # SQLAlchemy base and async session
├── models/       # SQLAlchemy ORM models and enums
├── schemas/      # Pydantic request and response schemas
├── services/     # Application and business logic
├── utils/        # Shared helpers such as pagination
└── main.py       # FastAPI application entry point
alembic/          # Database migration configuration and revisions
tests/            # Automated tests
```

## License

This project is licensed under the [MIT License](LICENSE).

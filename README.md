# Story Platform API

An asynchronous REST API for publishing short stories and managing their authors.

[![Build status](https://img.shields.io/badge/build-not%20configured-lightgrey)](https://github.com/nouvalkaff/story-platform-api/actions)
[![License: MIT](https://img.shields.io/github/license/nouvalkaff/story-platform-api)](LICENSE)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)

## Overview

Story Platform API provides account, authentication, and short-story workflows for clients that need a JSON-based publishing backend. It supports public discovery of published stories, authenticated author operations, and role-aware user administration. The application exposes versioned FastAPI routes backed by asynchronous SQLAlchemy sessions and PostgreSQL.

## Tech Stack

| Component | Version | Purpose |
| --- | --- | --- |
| Python | `>=3.13` | Application runtime |
| FastAPI | `>=0.141.1` | REST API and OpenAPI generation |
| PostgreSQL | Not pinned | Relational data store |
| SQLAlchemy | `>=2.0.52` | Async ORM and database access |
| asyncpg | `>=0.31.0` | Async PostgreSQL driver |
| Pydantic Settings | `>=2.15.0` | Validation and environment configuration |
| Alembic | `>=1.19.1` | Database migrations |
| python-jose | `>=3.5.0` | JWT encoding and validation |
| Passlib / bcrypt | `>=1.7.4` / `>=4.0.1,<4.1` | Password hashing |
| uv | Lockfile format `1`, revision `3` | Dependency and virtual-environment management |

## Features

- Authenticate users with expiring JWT bearer tokens.
- Register and manage user profiles, passwords, and account lifecycle.
- Enforce owner and administrator permissions on protected resources.
- Create, update, retrieve, and delete short stories.
- Publish or return stories to draft while tracking publication timestamps.
- Browse paginated published stories and search titles case-insensitively.
- Validate genres, content length, unique titles, and up to 10 normalized tags.
- Evolve the PostgreSQL schema through versioned Alembic migrations.

## Prerequisites

- Python `3.13` or later; the repository pins the development runtime to `3.13`.
- [uv](https://docs.astral.sh/uv/) `0.12.5` or a compatible release.
- A reachable PostgreSQL server; this project does not declare a required server version.

## Getting Started

1. Clone the repository.

   ```bash
   git clone https://github.com/nouvalkaff/story-platform-api.git
   cd story-platform-api
   ```

2. Install the locked dependencies.

   ```bash
   uv sync --frozen
   ```

3. Create the default database, or use an existing PostgreSQL database and adjust `DATABASE_URL` in the next step.

   ```sql
   CREATE DATABASE story_platform;
   ```

4. Create `.env` in the repository root.

   ```dotenv
   ENVIRONMENT=development
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/story_platform
   SECRET_KEY=dev-only-secret-key-32-characters
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

5. Apply the database migrations.

   ```bash
   uv run alembic upgrade head
   ```

6. Start the development server.

   ```bash
   uv run fastapi dev app/main.py
   ```

The API is available at `http://127.0.0.1:8000`. Interactive OpenAPI documentation is served at `http://127.0.0.1:8000/docs`, with ReDoc at `http://127.0.0.1:8000/redoc`.

## Environment Variables

| Variable | Required | Description | Example |
| --- | --- | --- | --- |
| `ENVIRONMENT` | Yes | Runtime mode. Accepted values are `development` and `production`; development mode enables SQL query logging. | `development` |
| `DATABASE_URL` | No | SQLAlchemy async PostgreSQL connection URL. | `postgresql+asyncpg://postgres:postgres@localhost:5432/story_platform` |
| `SECRET_KEY` | Yes | Secret used to sign and validate JWT access tokens. Use a strong random value outside local development. | `dev-only-secret-key-32-characters` |
| `ALGORITHM` | No | JWT signing algorithm. | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Access-token lifetime in minutes. | `60` |

## API Reference

All versioned endpoints use the `/api/v1` prefix. Protected endpoints require an `Authorization` header using the `Bearer` scheme.

For ready-to-run requests and examples, see the [Postman Documentation](https://documenter.getpostman.com/view/23758510/2sBYAuQqFF).

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/` | Public | Return the API welcome response. |
| `GET` | `/health` | Public | Return service health status. |
| `POST` | `/api/v1/auth/login` | Public | Authenticate an email and password and issue a JWT. |
| `POST` | `/api/v1/users/create` | Optional bearer; admin if supplied | Create a user account. |
| `GET` | `/api/v1/users/me` | Bearer | Return the current user's profile. |
| `GET` | `/api/v1/users/all` | Admin | List active and/or inactive users. |
| `PATCH` | `/api/v1/users/{user_id}` | Owner or admin | Update a user's email or full name; admins cannot change another user's email. |
| `PATCH` | `/api/v1/users/change-password/{user_id}` | Owner | Change the account password after verifying the old password. |
| `DELETE` | `/api/v1/users/sdelete/{user_id}` | Owner or admin | Deactivate a user account. |
| `DELETE` | `/api/v1/users/hdelete/{user_id}` | Owner | Permanently delete an account; `is_agree=true` confirms deletion when stories exist. |
| `POST` | `/api/v1/story/add` | Bearer | Create a draft story for the current user. |
| `GET` | `/api/v1/story/user/{user_id}` | Bearer | List a user's stories with `page` and `page_limit`; non-owners see published stories only. |
| `GET` | `/api/v1/story/published` | Public | List published stories with `page`, `size`, and optional title query `q`. |
| `PATCH` | `/api/v1/story/{story_id}/status` | Owner or admin | Set a story's status to `draft` or `published`. |
| `PATCH` | `/api/v1/story/{story_id}` | Owner or admin | Update one or more editable story fields. |
| `DELETE` | `/api/v1/story/{story_id}` | Owner | Permanently delete a story. |
| `GET` | `/api/v1/story/{story_id}` | Public | Return a published story; draft content is not exposed. |

Supported genres are `unspecified`, `romance`, `horror`, `mystery`, `fantasy`, `sci-fi`, `adventure`, and `drama`.


Story constraints:

  

- Titles must be unique and fit the 100-character database column.

- Content must contain 1–20,000 characters.

- Synopsis is optional and limited to 500 characters.

- A story may have up to 10 tags with a combined serialized length of 200 characters.

- New stories are created as `draft`; publication is handled through the status endpoint.

  

### Create a Story

  

Request:

  

```bash

curl -X POST http://localhost:8000/api/v1/story/add \

  -H "Authorization: Bearer <access-token>" \

  -H "Content-Type: application/json" \

  -d '{

    "title": "The Lighthouse Beyond the Fog",

    "content": "Mara reached the abandoned lighthouse before the storm and found its lamp still burning, although nobody had lived there for decades.",

    "synopsis": "A sailor discovers why an abandoned lighthouse continues to guide lost ships.",

    "genre": "mystery",

    "tags": ["lighthouse", "ocean", "mystery"]

  }'

```

  

Response (`201 Created`):

  

```json

{

  "status_code": 201,

  "status": true,

  "message": "Story created successfully",

  "data": {

    "title": "The Lighthouse Beyond the Fog",

    "content": "Mara reached the abandoned lighthouse before the storm and found its lamp still burning, although nobody had lived there for decades.",

    "synopsis": "A sailor discovers why an abandoned lighthouse continues to guide lost ships.",

    "genre": "mystery",

    "tags": ["lighthouse", "ocean", "mystery"],

    "id": 21,

    "status": "draft",

    "author_id": 2,

    "published_at": null,

    "created_by": 2,

    "created_at": "2026-08-27T09:00:00Z",

    "updated_by": 2,

    "updated_at": "2026-08-27T09:00:00Z"

  }

}

```

  

### Publish a Story

  

Request:

  

```bash

curl -X PATCH http://localhost:8000/api/v1/story/21/status \

  -H "Authorization: Bearer <access-token>" \

  -H "Content-Type: application/json" \

  -d '{"status": "published"}'

```

  

Response (`200 OK`):

  

```json

{

  "status_code": 200,

  "status": true,

  "message": "Story published successfully",

  "data": {

    "id": 21,

    "title": "The Lighthouse Beyond the Fog",

    "status": "published",

    "published_at": "2026-08-27T09:05:00Z"

  }

}

```

  

### List Published Stories

  

Request:

  

```bash

curl "http://localhost:8000/api/v1/story/published?page=1&size=5&q=lighthouse"

```

  

Response (`200 OK`):

  

```json

{

  "status_code": 200,

  "status": true,

  "message": "Success",

  "data": {

    "total": 1,

    "page": 1,

    "size": 5,

    "stories": [

      {

        "title": "The Lighthouse Beyond the Fog",

        "content": "Mara reached the abandoned lighthouse before the storm and found its lamp still burning, although nobody had lived there for decades.",

        "synopsis": "A sailor discovers why an abandoned lighthouse continues to guide lost ships.",

        "genre": "mystery",

        "tags": ["lighthouse", "ocean", "mystery"],

        "status": "published",

        "published_at": "2026-08-27T09:05:00Z"

      }

    ]

  }

}

```

## Project Structure

```text
story-platform-api/
├── alembic/
│   ├── versions/          # Ordered database migration revisions
│   ├── env.py             # Async migration environment
│   └── script.py.mako     # Migration template
├── app/
│   ├── api/
│   │   ├── v1/            # Authentication, user, and story routes
│   │   └── deps.py        # JWT and authorization dependencies
│   ├── core/              # Settings, security, logging, and error handling
│   ├── crud/              # SQLAlchemy persistence operations
│   ├── db/                # Declarative base and async sessions
│   ├── models/            # User and story ORM models
│   ├── schemas/           # Pydantic request and response models
│   ├── services/          # Authentication and story business logic
│   ├── utils/             # Formatting and pagination helpers
│   └── main.py            # FastAPI application entry point
├── tests/                 # Test module stubs
├── alembic.ini            # Alembic configuration
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Reproducible dependency lockfile
└── LICENSE                # MIT license text
```

## Contributing

Create branches from `main` using the `type/short-description` pattern—for example, `feat/add-story-filter`. Use `feat`, `fix`, `docs`, `refactor`, `test`, or `chore` as the type. Keep changes focused, add an Alembic revision for schema changes, and verify the application imports successfully:

```bash
uv run python -m compileall app
```

Push the branch to your fork and open a pull request against `main`. Describe the behavior change, document any API or migration impact, and request review before merging.

## License

This project is licensed under the [MIT License](LICENSE).

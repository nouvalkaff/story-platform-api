# 📚 Story Platform API

An asynchronous REST API for publishing short stories, managing authors, and exposing public story discovery endpoints — built with FastAPI and PostgreSQL.

<p align="left">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python&logoColor=white" alt="Python 3.13+"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-database-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white" alt="Docker"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Docker Compose](#docker-compose)
- [API Documentation](#api-documentation)
- [Endpoint Overview](#endpoint-overview)
- [License](#license)

---

## Overview

Story Platform API is a FastAPI backend for account management and short-story publishing. Authors can create and manage drafts, publish stories, and control their accounts. Public clients can browse published stories, search by title, and retrieve story details without authentication.

The API uses asynchronous SQLAlchemy sessions with PostgreSQL, JWT bearer authentication, role-based access control, and Alembic migrations.

## Features

- 🔐 JWT authentication with configurable token expiration
- 👤 User and administrator roles with owner-aware authorization
- 📝 User registration, profile updates, password changes, and account deletion
- 📖 Story creation, editing, deletion, and draft/published status management
- 🔍 Paginated public story discovery with case-insensitive title search
- 🎯 Public story lookup by numeric ID or exact title
- ✍️ Author names included in public story responses
- ✅ Validation for content, genres, unique titles, and normalized tags
- 🗄️ Versioned PostgreSQL schema migrations and idempotent development seed data

## Tech Stack

| Component               | Purpose                                          |
| ----------------------- | ------------------------------------------------ |
| Python `3.13+`          | Runtime                                          |
| FastAPI                 | REST API and OpenAPI documentation               |
| PostgreSQL              | Primary database                                 |
| SQLAlchemy 2            | Async ORM and database access                    |
| asyncpg / psycopg       | Async application and sync seed database drivers |
| Alembic                 | Database migrations                              |
| Pydantic Settings       | Environment configuration and validation         |
| python-jose             | JWT signing and verification                     |
| Passlib / bcrypt        | Password hashing                                 |
| uv                      | Dependency and virtual environment management    |
| Docker / Docker Compose | Containerized runtime and local services         |

Dependency constraints are defined in [`pyproject.toml`](pyproject.toml), with reproducible versions locked in [`uv.lock`](uv.lock).

## Project Structure

```text
story-platform-api/
├── alembic/              # Migration environment and revision files
├── app/
│   ├── api/              # FastAPI dependencies and versioned routes
│   ├── core/             # Configuration, security, logging, and errors
│   ├── crud/             # Database query and persistence operations
│   ├── db/               # SQLAlchemy engine, sessions, and base model
│   ├── models/           # ORM models
│   ├── schemas/          # Request and response models
│   ├── services/         # Application business logic
│   └── main.py           # FastAPI application entry point
├── docker/               # Container startup and database readiness scripts
├── seeds/                # Idempotent development seed data
├── tests/                # Test modules
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

## Prerequisites

- Python `3.13` or later
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL, unless using Docker Compose
- Docker and Docker Compose, for the containerized setup

## Local Setup

1. Clone the repository and enter the project directory.

   ```bash
   git clone https://github.com/nouvalkaff/story-platform-api.git
   cd story-platform-api
   ```

2. Install the locked dependencies.

   ```bash
   uv sync --frozen
   ```

3. Create a PostgreSQL database named `story_platform`, or use another existing database.

4. Create `.env` in the repository root.

   ```dotenv
   ENVIRONMENT=development
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/story_platform
   SECRET_KEY=replace-with-a-long-random-secret
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

5. Apply the migrations.

   ```bash
   uv run alembic upgrade head
   ```

6. Optionally load the development seed users and stories.

   ```bash
   uv run python -m seeds.run_all
   ```

7. Start the development server.

   ```bash
   uv run fastapi dev app/main.py
   ```

The API is available at `http://127.0.0.1:8000`.

## Environment Variables

| Variable                      | Required | Default              | Description                                                                                                        |
| ----------------------------- | -------- | -------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `ENVIRONMENT`                 | Yes      | None                 | Runtime mode: `development` or `production`. Development enables SQL query logging.                                |
| `DATABASE_URL`                | No       | Local PostgreSQL URL | SQLAlchemy URL using the `postgresql+asyncpg` driver. Set it explicitly for deployments and non-default databases. |
| `SECRET_KEY`                  | Yes      | None                 | Secret used to sign and validate JWT access tokens. Use a strong random value in production.                       |
| `ALGORITHM`                   | No       | `HS256`              | JWT signing algorithm.                                                                                             |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No       | `60`                 | Access-token lifetime in minutes.                                                                                  |

> ⚠️ Database passwords embedded in `DATABASE_URL` must be URL-encoded when they contain reserved URL characters.

Docker Compose additionally uses these variables for its PostgreSQL service:

| Variable            | Example          | Description                                                |
| ------------------- | ---------------- | ---------------------------------------------------------- |
| `POSTGRES_DB`       | `story_platform` | Database created by the PostgreSQL container.              |
| `POSTGRES_USER`     | `postgres`       | PostgreSQL user.                                           |
| `POSTGRES_PASSWORD` | `postgres`       | PostgreSQL password. Replace it outside local development. |

## Database Migrations

Apply all pending revisions:

```bash
uv run alembic upgrade head
```

Create a migration after changing ORM models:

```bash
uv run alembic revision --autogenerate -m "describe the change"
```

Roll back the most recent revision:

```bash
uv run alembic downgrade -1
```

Migration commands read `DATABASE_URL` through the same application settings as the API.

## Docker Compose

Docker Compose starts PostgreSQL, runs Alembic migrations, and then starts the API on port `8000`.

1. Create the Docker environment file from the tracked template.

   ```bash
   cp .env.docker.example .env.docker
   ```

2. To use the PostgreSQL container included in `docker-compose.yml`, set these values in `.env.docker`:

   ```dotenv
   ENVIRONMENT=development
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/story_platform
   SECRET_KEY=replace-with-a-long-random-secret
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60

   POSTGRES_DB=story_platform
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   ```

   The tracked template also demonstrates an external Supabase connection. Set `DATABASE_URL` to the database the API should actually use.

3. Build and start the services.

   ```bash
   docker compose up --build
   ```

The API is then available at `http://localhost:8000`. The container entry point applies migrations and runs the idempotent seed scripts during startup. Review the data in `seeds/` before using that startup flow in production.

Stop the services with:

```bash
docker compose down
```

> The named PostgreSQL volume is retained unless it is explicitly removed.

## API Documentation

When the application is running:

| Resource           | URL                                                                              |
| ------------------ | -------------------------------------------------------------------------------- |
| Swagger UI         | `http://localhost:8000/docs`                                                     |
| ReDoc              | `http://localhost:8000/redoc`                                                    |
| OpenAPI schema     | `http://localhost:8000/openapi.json`                                             |
| Postman collection | [Story Platform API](https://documenter.getpostman.com/view/23758510/2sBYAuSWf2) |
| Health check       | `http://localhost:8000/health`                                                   |

Protected endpoints require the following header:

```http
Authorization: Bearer <access-token>
```

All versioned routes use the `/api/v1` prefix.

## Endpoint Overview

| Method   | Endpoint                                  | Access                       | Purpose                                                               |
| -------- | ----------------------------------------- | ---------------------------- | --------------------------------------------------------------------- |
| `GET`    | `/`                                       | Public                       | API welcome response.                                                 |
| `GET`    | `/health`                                 | Public                       | Service health check.                                                 |
| `POST`   | `/api/v1/auth/login`                      | Public                       | Authenticate and issue a bearer token.                                |
| `POST`   | `/api/v1/users/create`                    | Public; admin token optional | Create a user account.                                                |
| `GET`    | `/api/v1/users/me`                        | Authenticated                | Return the current user.                                              |
| `GET`    | `/api/v1/users/all`                       | Admin                        | List active and/or inactive users.                                    |
| `PATCH`  | `/api/v1/users/{user_id}`                 | Owner or admin               | Update email or full name.                                            |
| `PATCH`  | `/api/v1/users/change-password/{user_id}` | Owner                        | Change a password.                                                    |
| `DELETE` | `/api/v1/users/sdelete/{user_id}`         | Owner or admin               | Deactivate an account.                                                |
| `DELETE` | `/api/v1/users/hdelete/{user_id}`         | Owner                        | Permanently delete an account.                                        |
| `POST`   | `/api/v1/story/add`                       | Authenticated                | Create a draft story.                                                 |
| `GET`    | `/api/v1/story/user/{user_id}`            | Authenticated                | List a user's stories with pagination.                                |
| `GET`    | `/api/v1/story/published`                 | Public                       | List published stories; supports `page`, `size`, and title query `q`. |
| `GET`    | `/api/v1/story/details/{param}`           | Public                       | Get a published story by numeric ID or exact title.                   |
| `PATCH`  | `/api/v1/story/{story_id}/status`         | Owner or admin               | Change status to `draft` or `published`.                              |
| `PATCH`  | `/api/v1/story/{story_id}`                | Owner or admin               | Update a story.                                                       |
| `DELETE` | `/api/v1/story/{story_id}`                | Owner                        | Permanently delete a story.                                           |

Story genres are `unspecified`, `romance`, `horror`, `mystery`, `fantasy`, `sci-fi`, `adventure`, and `drama`.

## License

This project is licensed under the [MIT License](LICENSE).

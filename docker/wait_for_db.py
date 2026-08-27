import asyncio
import os

import asyncpg
from sqlalchemy.engine import make_url

MAX_ATTEMPTS = 30
RETRY_DELAY_SECONDS = 2


def database_dsn(database_url: str) -> str:
    """Convert SQLAlchemy's async URL to a DSN accepted by asyncpg."""
    return (
        make_url(database_url)
        .set(drivername="postgresql")
        .render_as_string(hide_password=False)
    )


async def wait_for_database() -> None:
    database_url = database_dsn(os.environ["DATABASE_URL"])

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            connection = await asyncpg.connect(database_url)
            await connection.close()
            print("Database connection established.", flush=True)
            return
        except asyncpg.InvalidPasswordError as error:
            raise RuntimeError(
                "PostgreSQL rejected the credentials. Set POSTGRES_PASSWORD to "
                "the password used when the postgres_data volume was initialized, "
                "then recreate the volume if this is disposable development data."
            ) from error
        except (OSError, asyncpg.PostgresError) as error:
            if attempt == MAX_ATTEMPTS:
                raise RuntimeError(
                    f"Database did not become available after {MAX_ATTEMPTS} attempts."
                ) from error

            print(
                f"Database is not ready (attempt {attempt}/{MAX_ATTEMPTS}): {error}",
                flush=True,
            )
            await asyncio.sleep(RETRY_DELAY_SECONDS)


if __name__ == "__main__":
    asyncio.run(wait_for_database())

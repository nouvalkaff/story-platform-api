import sys

from seeds.seed_stories import seed_stories
from seeds.seed_users import seed_users


def main() -> None:
    try:
        print("Seeding users...", end=" ")
        seed_users()
        print("done")

        print("Seeding stories...", end=" ")
        seed_stories()
        print("done")
    except Exception as error:
        print(f"Seeding failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()

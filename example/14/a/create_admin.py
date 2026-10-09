"""Make a user an admin.

    python create_admin.py <username>

If the user exists, they're promoted. If not, you're asked for a password
and the account is created as an admin. The API never lets anyone sign
up as admin, so on a real shop (no seed data) this is how you get the
first one.
"""
import sys
from getpass import getpass

import crud
import main  # noqa: F401  (creates the tables first)
from database import SessionLocal


def run(username: str) -> None:
    with SessionLocal() as db:
        user = crud.get_user_by_username(db, username)
        if user is not None:
            user.role = "admin"
            db.commit()
            print(f'"{username}" is now an admin.')
            return

        password = getpass(f'New password for "{username}" (min 8 chars): ')
        if len(password) < 8:
            sys.exit("Password too short.")
        crud.create_user(db, username, password, role="admin")
        print(f'Admin "{username}" created.')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python create_admin.py <username>")
    run(sys.argv[1])

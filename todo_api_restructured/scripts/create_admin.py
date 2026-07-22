"""Create or promote an administrator from the command line."""

import argparse
import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, UserRole


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("email", help="Administrator email address")
    args = parser.parse_args()
    email = args.email.strip().lower()
    password = getpass.getpass("Password (8-128 characters): ")
    if len(password) > 128:
        parser.error("Password must not exceed 128 characters")

    with SessionLocal.begin() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user:
            user.role = UserRole.ADMIN
            user.hashed_password = hash_password(password)
            print(f"Promoted {email} and updated its password.")
        else:
            db.add(
                User(
                    email=email,
                    hashed_password=hash_password(password),
                    role=UserRole.ADMIN,
                    is_email_verified=True,
                )
            )
            print(f"Created administrator {email}.")


if __name__ == "__main__":
    main()

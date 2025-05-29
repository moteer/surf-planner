from app.api.students_router import transform_students
from app.core.db import get_db
from datetime import date
from fastapi import Query
import os


def main():
    # Manually simulate dependency injection for DB session
    session = next(get_db())

    # Call the function
    response = transform_students(
        session=session
    )

    print("✅ Done")


if __name__ == "__main__":
    main()

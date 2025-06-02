import raw_csv_insert
import sys
import os

# Add the project root to sys.path so 'app' can be imported
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from app.api.students_router import transform_students
from app.core.db import get_db


def main():
    # reads
    raw_csv_insert.csv_insert("csvs/2025-05-30-surf-plan.csv")

    # Manually simulate dependency injection for DB session
    session = next(get_db())

    # Call the function
    response = transform_students(
        session=session
    )


if __name__ == "__main__":
    main()

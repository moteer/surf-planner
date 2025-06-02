from fastapi import UploadFile
from app.core.db import get_db
import tempfile
import raw_csv_insert
import transformer


class StudentService:

    def __init__(self, student_repository: StudentRepositoryInterface):
        self.student_repository = student_repository
        self.students = []

def import_csv_file(file: UploadFile):
    session = next(get_db())

    # Save to a temp file and pass to existing import logic
    with tempfile.NamedTemporaryFile(delete=True, suffix=".csv") as tmp:
        tmp.write(file.file.read())
        tmp.flush()
        raw_csv_insert.csv_insert(tmp.name)
        transform_students(session=session)

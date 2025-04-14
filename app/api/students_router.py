from datetime import date
from typing import Annotated, Optional
from app.core.db import get_db
from app.data.sql_alchemey_repository_impl import SQLAlchemyStudentRepository
from app.services.student_service import StudentService
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

router = APIRouter()

# alle studenten als json
# ranges
@router.get("/students")
def get_students(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    session: Session = Depends(get_db)):

    student_service = StudentService(SQLAlchemyStudentRepository(session))

    if start_date and end_date:
        return student_service.get_students_by_date_range(start_date, end_date)

    return student_service.get_all_students()


# http://127.0.0.1:8000/students/?start_date=somestart&end_date=someend
@router.get("/students/")
def read_items(start_date, end_date):
    print(start_date)
    print(end_date)

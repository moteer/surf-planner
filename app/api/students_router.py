from datetime import date
from typing import Annotated, Optional
from app.core.db import get_db
from app.data.sql_alchemey_repository_impl import SQLAlchemyStudentRepositoryImpl, SQLAlchemyBookingRawRepositoryImpl
from app.services.student_service import StudentService
from app.services.student_transformer_service import StudentTransformerService
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
    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))

    if start_date and end_date:
        return student_service.get_students_by_date_range(start_date, end_date)

    return student_service.get_all_students()


# http://127.0.0.1:8000/students/?start_date=somestart&end_date=someend
@router.get("/students/")
def read_items(start_date, end_date):
    print(start_date)
    print(end_date)


@router.get("/transform/student")
def get_students(session: Session = Depends(get_db)):

    student_transformer_service = StudentTransformerService(SQLAlchemyBookingRawRepositoryImpl(session),
                                                            SQLAlchemyStudentRepositoryImpl(session))

    student_transformer_service.transform_all_bookings_into_students()

    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))
    return student_service.get_all_students()

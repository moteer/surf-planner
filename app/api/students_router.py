import pandas as pd
from collections import defaultdict
from datetime import date
from fastapi import APIRouter, Depends, Query, Response, UploadFile, File, HTTPException
from io import BytesIO
from sqlalchemy.orm import Session
from typing import Optional

from app.core.db import get_db
from app.data.sql_alchemey_repository_impl import SQLAlchemyStudentRepositoryImpl, SQLAlchemyBookingRawRepositoryImpl
from app.data.sql_alchemey_repository_impl import SQLAlchemySurfPlanRepositoryImpl
from app.services.student_service import StudentService
from app.services.surf_plan_service import SurfPlanService
from app.services.tide_service_interface import TideServiceMockImpl
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.student_transformer_service import StudentTransformerService

router = APIRouter()

@router.get("/test-cors")
def test_cors():
    return {"message": "CORS works"}

@router.post("/import-bookings")
async def import_bookings(file: UploadFile = File(...),
                          session: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    try:
        student_transformer_service = \
            StudentTransformerService(SQLAlchemyBookingRawRepositoryImpl(session),
                                      SQLAlchemyStudentRepositoryImpl(session))
        student_transformer_service.import_csv_file(file)
        return {"message": "CSV imported successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/bookings")
def get_diets_of_guests_per_day(date: Optional[date] = Query(None),
                                session: Session = Depends(get_db)):
    booking_repository = SQLAlchemyBookingRawRepositoryImpl(session)
    return [booking for booking in booking_repository.get_for_date(date, date) if booking.booking_status != "cancelled"]


@router.get("/students/oncamp")
def get_surf_plan(date: Optional[date] = date.today(),
                  session: Session = Depends(get_db)):
    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))
    return student_service.get_all_students_for_date(date)


# ranges
@router.get("/surfplan")
def get_surf_plan(plan_date: Optional[date] = date.today(),
                  session: Session = Depends(get_db)):
    surf_plan_service = SurfPlanService(
        SQLAlchemySurfPlanRepositoryImpl(session),
        StudentService(SQLAlchemyStudentRepositoryImpl(session)),
        TideServiceMockImpl())

    return surf_plan_service \
        .generate_surf_plan_for_day(plan_date if plan_date is not None else date.today())


def get_students(
        start_date: Optional[date] = date.today(),
        end_date: Optional[date] = date.today(),
        session: Session = Depends(get_db)):
    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))

    if start_date and end_date:
        return student_service.get_students_with_booked_lessons_by_date_range(start_date, end_date)

    return student_service.get_all_students()


@router.get("/students/export")
def export_students_to_excel(
        date: Optional[date] = date.today(),
        session: Session = Depends(get_db)):
    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))

    if date:
        students = student_service.get_students_with_booked_lessons_by_date_range(date, date)
    else:
        students = student_service.get_all_students()

    # Grouping logic
    beginner = []
    beginner_plus = []
    intermediate = []
    advanced = []
    teens = []
    kids = []
    not_booked = []

    for student in students:
        age_group = student.age_group.lower() if student.age_group else "adult"

        if student.number_of_surf_lessons == 0:
            not_booked.append(student)
        elif 'teen' in age_group:
            teens.append(student)
        elif 'kid' in age_group:
            kids.append(student)
        else:
            level = (student.level or "BEGINNER").strip().upper()
            if level == "BEGINNER":
                beginner.append(student)
            elif level == "BEGINNER PLUS":
                beginner_plus.append(student)
            elif level == "INTERMEDIATE":
                intermediate.append(student)
            elif level == "ADVANCED":
                advanced.append(student)
            else:
                beginner.append(student)  # fallback to beginner

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        def write_sheet(name, students_list):
            df = pd.DataFrame([{
                "first name": s.first_name,
                "last name": s.last_name,
                "age group": s.age_group,
                "birthday": s.birthday,
                "gender": s.gender,
                "booking bumber": s.booking_number,
                "arrival": s.arrival,
                "departure": s.departure,
                "number of surflessons booked": s.number_of_surf_lessons,
                "level": s.level
            } for s in students_list])
            df.to_excel(writer, sheet_name=name, index=False)

        if beginner:
            write_sheet("BEGINNER", beginner)
        if beginner_plus:
            write_sheet("BEGINNER PLUS", beginner_plus)
        if intermediate:
            write_sheet("INTERMEDIATE", intermediate)
        if advanced:
            write_sheet("ADVANCED", advanced)
        if teens:
            write_sheet("Teens", teens)
        if kids:
            write_sheet("Kids", kids)

    output.seek(0)
    return Response(
        content=output.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=" + date.strftime("%Y-%m-%d") + "-surf-plan-export.xlsx"}
    )


@router.get("/students/export/html", response_class=Response)
def export_students_as_html(
        date: Optional[date] = Query(None),
        session: Session = Depends(get_db)):
    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))

    if date:
        students = student_service.get_students_with_booked_lessons_by_date_range(date, date)
    else:
        students = student_service.get_all_students()

    groups = defaultdict(list)

    for student in students:
        age_group = student.age_group.lower() if student.age_group else "adult"

        if student.number_of_surf_lessons == 0:
            groups["Not booked"].append(student)
        elif 'teen' in age_group:
            groups["Teens"].append(student)
        elif 'kid' in age_group:
            groups["Kids"].append(student)
        else:
            level = (student.level or "BEGINNER").strip().upper()
            if level not in ["BEGINNER", "BEGINNER PLUS", "INTERMEDIATE", "ADVANCED"]:
                level = "BEGINNER"
            groups[level].append(student)

    html = "<html><head><title>Students Export</title></head><body>"
    for group_name, group_students in groups.items():
        df = pd.DataFrame([{
            "first name": s.first_name,
            "last name": s.last_name,
            "age group": s.age_group,
            "birthday": s.birthday,
            "gender": s.gender,
            "booking bumber": s.booking_number,
            "arrival": s.arrival,
            "departure": s.departure,
            "number of surflessons booked": s.number_of_surf_lessons,
            "level": s.level
        } for s in group_students])
        html += f"<h2>{group_name}</h2>"
        html += df.to_html(index=False)

    html += "</body></html>"
    return html


@router.get("/transform/students")
def transform_students(session: Session = Depends(get_db)):
    student_transformer_service.transform_all_bookings_to_students()
    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))
    return student_service.get_all_students()

import pandas as pd
from collections import defaultdict
from datetime import date, timedelta, datetime
from fastapi import APIRouter, Depends, Query, Response, UploadFile, File, HTTPException
from io import BytesIO
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.responses import StreamingResponse
from app.core.db import get_db
from app.data.sql_alchemey_repository_impl import SQLAlchemyStudentRepositoryImpl, SQLAlchemyBookingRawRepositoryImpl
from app.data.sql_alchemey_repository_impl import SQLAlchemySurfPlanRepositoryImpl
from app.services.student_service import StudentService
from app.services.surf_plan_service import SurfPlanService
from app.services.tide_service_interface import TideServiceMockImpl
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.student_transformer_service import StudentTransformerService

from app.domain.models import SurfPlan, Slot, Group

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
    return [booking for booking in booking_repository.get_for_date(date, date) if
            booking.booking_status != "cancelled" and booking.booking_status != "expired"]


@router.get("/upcomingweek")
def get_diets_summary_of_next_week(date: Optional[date] = Query(None),
                                   session: Session = Depends(get_db)):
    def next_sunday(d: date) -> date:
        days_ahead = (6 - d.weekday()) % 7  # Sunday is 6
        return d + timedelta(days=days_ahead)

    def next_saturday_after_sunday(d: date) -> date:
        sunday = next_sunday(d)
        return sunday + timedelta(days=6)

    # Example usage

    upcoming_sunday = next_sunday(date)
    upcoming_saturday = next_saturday_after_sunday(date)

    print(f"for {upcoming_sunday}")

    booking_repository = SQLAlchemyBookingRawRepositoryImpl(session)
    bookings = [booking for booking in booking_repository.get_for_date_inclusive(upcoming_sunday, upcoming_saturday) if
                booking.booking_status != "cancelled" and booking.booking_status != "expired"]
    print(f"😱 {len(bookings)}")

    def filter_and_sum_people(date):
        sum_for_date = sum(
            1 for b in bookings
            if b.arrival <= date <= b.departure
        )
        print(f"{date}: {sum_for_date}")
        return sum_for_date

    monday = upcoming_sunday + timedelta(days=1)
    tuesday = upcoming_sunday + timedelta(days=2)
    wednesday = upcoming_sunday + timedelta(days=3)
    thursday = upcoming_sunday + timedelta(days=4)
    friday = upcoming_sunday + timedelta(days=5)
    saturday = upcoming_sunday + timedelta(days=6)
    return {"upcoming_week":
                {"starting_date": upcoming_sunday,
                 "end_date": upcoming_saturday,
                 "Sunday": {"date": upcoming_sunday, "total_amount": filter_and_sum_people(upcoming_sunday)},
                 "Monday": {"date": monday, "total_amount": filter_and_sum_people(monday)},
                 "Tuesday": {"date": tuesday, "total_amount": filter_and_sum_people(tuesday)},
                 "Wednesday": {"date": wednesday, "total_amount": filter_and_sum_people(wednesday)},
                 "Thursday": {"date": thursday, "total_amount": filter_and_sum_people(thursday)},
                 "Friday": {"date": friday, "total_amount": filter_and_sum_people(friday)},
                 "Saturday": {"date": saturday, "total_amount": filter_and_sum_people(saturday)},
                 }}


@router.get("/students/oncamp")
def get_surf_plan(date: Optional[date] = date.today(),
                  session: Session = Depends(get_db)):
    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))
    return student_service.get_all_students_for_date(date)


@router.get("/students")
def get_surf_plan(start: Optional[date] = date.today(),
                  end: Optional[date] = date.today(),
                  session: Session = Depends(get_db)):
    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))
    return student_service.get_students_with_booked_lessons_by_date_range(start, end)


# @router.get("/surfplan")
def get_surf_plan(plan_date: Optional[date] = date.today(),
                  session: Session = Depends(get_db)):
    surf_plan_service = SurfPlanService(
        SQLAlchemySurfPlanRepositoryImpl(session),
        StudentService(SQLAlchemyStudentRepositoryImpl(session)),
        TideServiceMockImpl())

    return surf_plan_service \
        .generate_surf_plan_for_day(plan_date if plan_date is not None else date.today())


def notIsSunday(sunday):
    return sunday.weekday() != 6


@router.get("/students/groups")
def surf_groups_for_week(sunday: date, session: Session = Depends(get_db)):
    if notIsSunday(sunday):
        return f"{sunday} is not a sunday!"

    surf_plan_service = SurfPlanService(
        SQLAlchemySurfPlanRepositoryImpl(session),
        StudentService(SQLAlchemyStudentRepositoryImpl(session)),
        TideServiceMockImpl())

    return surf_plan_service.generate_surf_groups_for_week(sunday);


@router.get("/surfplan")
def surf_groups_for_surf_plan(day: date, session: Session = Depends(get_db)):
    surf_plan_service = SurfPlanService(
        SQLAlchemySurfPlanRepositoryImpl(session),
        StudentService(SQLAlchemyStudentRepositoryImpl(session)),
        TideServiceMockImpl())

    surf_groups = surf_plan_service.generate_surf_groups_for_day(day)
    print(surf_groups)

    initial_sot_a_groups = [Group(level="Beginner A", age_group="Adults", students=surf_groups["beginner"]),
                            Group(level="Beginner Plus A", age_group="Adults", students=surf_groups["beginner_plus"]),
                            Group(level="Intermediate A", age_group="Adults", students=surf_groups["intermediate"]),
                            Group(level="Advanced A", age_group="Adults", students=surf_groups["advanced"]),
                            Group(level="Teens A", age_group="Teens", students=surf_groups["teens"]),
                            Group(level="Kids A", age_group="Kids", students=surf_groups["kids"])
                            ]

    initial_slot_b_groups = [Group(level="Beginner B", age_group="Adults", students=[]),
                             Group(level="Beginner Plus B", age_group="Adults", students=[]),
                             Group(level="Intermediate B", age_group="Adults", students=[]),
                             Group(level="Advanced B", age_group="Adults", students=[]),
                             Group(level="Teens B", age_group="Teens", students=[]),
                             Group(level="Kids B", age_group="Kids", students=[])
                             ]
    slots = [Slot(datetime.now(), initial_sot_a_groups), Slot(datetime.now(), initial_slot_b_groups)]
    return SurfPlan(plan_date=day, slots=slots, non_participating_guests=surf_groups["non_participating_guests"])


@router.get("/students/groups/export")
def export_students_to_excel(sunday: date, session: Session = Depends(get_db)):
    if notIsSunday(sunday):
        return f"{sunday} is not a sunday!"

    surf_plan_service = SurfPlanService(
        SQLAlchemySurfPlanRepositoryImpl(session),
        StudentService(SQLAlchemyStudentRepositoryImpl(session)),
        TideServiceMockImpl())
    surf_groups = surf_plan_service.generate_surf_groups_for_week(sunday)

    return create_excel_week_overview(sunday, surf_groups)

def create_excel_week_overview(sunday, surf_groups):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet("Weekly Plan")
        writer.sheets["Weekly Plan"] = worksheet

        weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        for i, day in enumerate(weekdays):
            date = sunday + timedelta(days=i)
            worksheet.write(0, i + 3, f"{day} ({date.strftime('%d.%m.%Y')})")

        row = 2
        for level in ["beginner", "beginner_plus", "intermediate", "advanced", "teens", "kids"]:
            students = surf_groups[level]
            if not students:
                continue

            worksheet.write(row, 0,
                            level.capitalize() if level in ["kids", "teens"] else level.replace("_",
                                                                                                " ").capitalize())
            row += 1
            worksheet.write_row(row, 0,
                                ["First Name", "Last Name", "Age", *weekdays, "Number of Booked Lessons", "Level",
                                 "Arrival", "Departure", "Tent"])
            row += 1

            for student in students:
                age = (datetime.now().date() - student.birthday).days // 365 if student.birthday else ""
                student_row = [
                    student.first_name,
                    student.last_name,
                    age,
                ]
                lesson_start = student.arrival + timedelta(days=1)
                planned_lessons = 0

                for i in range(7):
                    current_day = sunday + timedelta(days=i)
                    if lesson_start <= current_day < student.departure and planned_lessons < student.number_of_surf_lessons:
                        student_row.append(1)
                        planned_lessons += 1
                    else:
                        student_row.append("")

                student_row.extend([student.number_of_surf_lessons, level, student.arrival.strftime('%d.%m.%Y'),
                                    student.departure.strftime('%d.%m.%Y'), student.tent])
                worksheet.write_row(row, 0, student_row)
                row += 1

            row += 2

    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=weekly_surf_plan.xlsx"})


def get_students(
        start_date: Optional[date] = date.today(),
        end_date: Optional[date] = date.today(),
        session: Session = Depends(get_db)):
    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))

    if start_date and end_date:
        return student_service.get_students_with_booked_lessons_by_date_range(start_date, end_date)

    return student_service.get_all_students()


@router.get("/kids")
def get_kids(
        start: Optional[date] = date.today(),
        end: Optional[date] = date.today(),
        session: Session = Depends(get_db)):
    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))

    students = student_service.get_students_by_date_range(start, end)

    return [kid for kid in students if
            kid.age_group and kid.age_group != "" and kid.age_group != "Adults >18 years"]


@router.get("/students/export")
def export_students_to_excel(
        start: Optional[date] = date.today(),
        end: Optional[date] = date.today(),
        session: Session = Depends(get_db)):
    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))

    if start:
        students = student_service.get_students_with_booked_lessons_by_date_range(start, end)
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
            print("🧻")
            print(students_list[0].departure)
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
        headers={
            "Content-Disposition": "attachment; filename=" + start.strftime("%Y-%m-%d") + "-surf-plan-export.xlsx"}
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


# http://localhost:8000/bookings/export?start=2025-06-01&end=2025-06-07
@router.get("/bookings/export")
def export_students_to_excel(
        start: Optional[date] = date.today(),
        end: Optional[date] = date.today(),
        session: Session = Depends(get_db)):
    student_service = StudentService(SQLAlchemyStudentRepositoryImpl(session))
    print(f"start: {start}")
    print(f"end: {end}")
    booking_repository = SQLAlchemyBookingRawRepositoryImpl(session)

    bookings = booking_repository.get_for_date_inclusive(start, end)
    # [booking for booking in booking_repository.get_for_date_inclusive(start, end)
    # if
    # booking.booking_status != "cancelled"
    # and booking.booking_status != "expired"
    # and booking.number_of_surf_lessons > 0]

    # students = [student for student in student_service.get_students_with_booked_lessons_by_date_range(start, end)
    #            if student.booking_status != "cancelled" and student.booking_status != "expired"]
    print("🎉")
    print(len(bookings))
    print(bookings)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        def write_sheet(name, bookings):
            df = pd.DataFrame([{
                "first name": booking.first_name,
                "last name": booking.last_name,
                "age group": booking.group,
                "arrival": booking.arrival,
                "departure": booking.departure,
                "number of surflessons booked": booking.number_of_surf_lessons,
                "tent": booking.tent
            } for booking in bookings])
            df.to_excel(writer, sheet_name=name, index=False)

        write_sheet("Students", bookings)

    output.seek(0)
    return Response(
        content=output.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=start_" + start.strftime(
                "%Y-%m-%d") + "_end_" + end.strftime(
                "%Y-%m-%d") + "-students-export.xlsx"}
    )

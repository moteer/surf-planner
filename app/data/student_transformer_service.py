from datetime import datetime
from app.data.orm_models import StudentORM

def transform_student(raw_row) -> StudentORM:
    """Transforms a raw booking row into a StudentORM object."""
    try:
        return StudentORM(
            first_name=raw_row["Guest first name"],
            last_name=raw_row["Guest last name"],
            birthday=datetime.strptime(raw_row["Guest birthday"], "%Y-%m-%d").date(),
            gender=raw_row.get("Guest gender", "unknown"),
            age_group=determine_age_group(raw_row.get("Guest age")),
            level=raw_row.get("Guest level", "unknown"),
            booking_number=raw_row["Booking ID"]
        )
    except Exception as e:
        print(f"⚠️ Error transforming row {raw_row.get('Booking ID')}: {e}")
        return None

def determine_age_group(age_raw):
    """Converts age string or number into a group label."""
    try:
        age = int(float(age_raw))
        if age < 13:
            return "child"
        elif age < 18:
            return "teen"
        else:
            return "adult"
    except Exception:
        return "unknown"

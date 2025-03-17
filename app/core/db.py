from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database connection (update with your MySQL credentials)
DATABASE_URL = "mysql+pymysql://admin:admin@localhost/surf_conditions"

# Create engine and session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_database_session():
    database = SessionLocal()
    try:
        yield database  # Pass the session to the dependency
    finally:
        database.close()  # Ensure the session is properly closed

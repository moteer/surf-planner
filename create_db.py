# create_db.py
from app.core.db import engine, Base  # Import engine and Base from your db.py file
from app.data.orm_models import *    # Import your ORM models (tables) here
from app.core.db import create_schema  # If you have a function for schema creation

def recreate_db_schema():
    # Drop all tables (if they exist) and recreate them
    Base.metadata.drop_all(bind=engine)   # Optional: drops existing tables
    Base.metadata.create_all(bind=engine) # Creates the schema
    print("Database schema recreated successfully.")

if __name__ == "__main__":
    recreate_db_schema()

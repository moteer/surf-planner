from app.data.orm_models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

# Create the database engine
engine = create_engine(DATABASE_URL, connect_args={})

# Create session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)



# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    create_schema()

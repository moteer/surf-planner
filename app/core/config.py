import os

DATABASE_URL = os.getenv("DATABASE_URL")

print(f"DATABASE_URL: {DATABASE_URL}")

# if DB_TYPE == "sqlite":
#     DATABASE_URL = "sqlite:///:memory:"  # In-memory SQLite (for testing)
# elif DB_TYPE == "mysql":
#     DATABASE_URL = "mysql+pymysql://root:rootroot@localhost/surfplanner"
# else:
#     raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}")

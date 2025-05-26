import os

DB_USER = os.getenv("DB_USER")
DB_PW = os.getenv("DB_PW")
DATABASE_URL =  f"mysql+pymysql://{DB_USER}:{DB_PW}@localhost/sea_natives_surfplanner"

print(f"DATABASE_URL: {DATABASE_URL}")

# if DB_TYPE == "sqlite":
#     DATABASE_URL = "sqlite:///:memory:"  # In-memory SQLite (for testing)
# elif DB_TYPE == "mysql":
#     DATABASE_URL = "mysql+pymysql://root:rootroot@localhost/surfplanner"
# else:
#     raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}")

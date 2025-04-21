import os

# Get database type from environment variables (default: sqlite memory)
DB_TYPE = "mysql"

print(f"DB_TYPE: {DB_TYPE}")

if DB_TYPE == "sqlite":
    DATABASE_URL = "sqlite:///:memory:"  # In-memory SQLite (for testing)
elif DB_TYPE == "mysql":
    DATABASE_URL = "mysql+pymysql://root:rootroot@localhost/surfplanner"
else:
    raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}")

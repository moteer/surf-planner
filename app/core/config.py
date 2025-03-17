import os

# Get database type from environment variables (default: sqlite memory)
DB_TYPE = os.getenv("DB_TYPE")

if DB_TYPE == "sqlite":
    DATABASE_URL = "sqlite:///:memory:"  # In-memory SQLite (for testing)
elif DB_TYPE == "mysql":
    DATABASE_URL = "mysql+pymysql://admin:admin@localhost/surf_conditions"
else:
    raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}")

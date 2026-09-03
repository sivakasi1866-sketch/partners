import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

# Safe test strategy: if missing, application fails clearly or we leave it None
if not DATABASE_URL:
    print("WARNING: DATABASE_URL is not set. PostgreSQL connection will fail.")
    # Provide a dummy string so alembic doesn't crash on import, but connections will fail
    DATABASE_URL = "postgresql://user:pass@localhost/dbname"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv()

# URL.create escapes special characters (like "@") in the password.
# Set DATABASE_URL to override it (e.g. "sqlite:///./test.db").
DATABASE_URL = os.getenv("DATABASE_URL") or URL.create(
    "mysql+pymysql",
    username=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    host=os.getenv("MYSQL_HOST", "127.0.0.1"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    database=os.getenv("MYSQL_DB", "fastapi_learn"),
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

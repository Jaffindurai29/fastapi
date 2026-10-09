import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "fastapi_learn")

# Set DATABASE_URL directly to override everything above (e.g. to point
# at SQLite for a quick local test with no MySQL server at all).
#
# URL.create instead of an f-string: a password like "p@ss" would turn
# f"...:{password}@{host}..." into a URL with two "@", and the driver
# would try to connect to the host "ss@127.0.0.1". URL.create escapes it.
DATABASE_URL = os.getenv("DATABASE_URL") or URL.create(
    "mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=int(MYSQL_PORT),
    database=MYSQL_DB,
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

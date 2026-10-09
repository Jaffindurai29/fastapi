import os
import sys
import tempfile
from pathlib import Path

import pytest

# Run against a throwaway SQLite file, never your MySQL data. Must be set
# BEFORE main/database are imported. Set TEST_DATABASE_URL to run against
# an EMPTY MySQL database instead (SQLite ignores the row locks).
_db_file = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", f"sqlite:///{_db_file}")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

import crud  # noqa: E402
from database import SessionLocal  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def _login(client, username):
    res = client.post("/login", json={"username": username, "password": "password123"})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture(scope="session")
def admin(client):
    with SessionLocal() as db:
        crud.create_user(db, "boss", "password123", role="admin")
    return _login(client, "boss")


@pytest.fixture(scope="session")
def make_customer(client):
    def make(username):
        assert client.post("/register", json={"username": username, "password": "password123"}).status_code == 201
        return _login(client, username)

    return make

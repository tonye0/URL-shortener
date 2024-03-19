from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from .main import app


client = TestClient(app)


# Mocking the database session
@pytest.fixture
def mock_db_session():
    with patch('main.SessionLocal') as mock:
        mock.return_value = MagicMock()
        yield mock


def test_index():
    response = client.get("/url")
    assert response.status_code == 200


import pytest
from fastapi.testclient import TestClient

from fastzero.app import app


# Arrange
@pytest.fixture
def client():
    return TestClient(app)

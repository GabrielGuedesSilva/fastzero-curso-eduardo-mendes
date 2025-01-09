import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastzero.app import app
from fastzero.models import table_registry


# Arrange
@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')

    # Cria todas as definicções do banco e depois apaga tudo
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        # yield faz com que a função pare na linha abaixo retornando a session,
        # depois que o teste terminar, o código abaixo do yield é executado
        yield session

    table_registry.metadata.drop_all(engine)

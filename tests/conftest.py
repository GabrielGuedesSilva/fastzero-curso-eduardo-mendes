import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fastzero.app import app
from fastzero.database import get_session
from fastzero.models import User, table_registry


# Arrange
@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    # Cria todas as definicções do banco e depois apaga tudo
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        # yield faz com que a função pare na linha abaixo retornando a session,
        # depois que o teste terminar, o código abaixo do yield é executado
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    user = User(username='test user', email='test@email.com', password='12345')
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

from contextlib import contextmanager
from datetime import datetime

import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fastzero.app import app
from fastzero.database import get_session
from fastzero.models import Task, TaskState, User, table_registry
from fastzero.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'senha-{obj.username}')


class TaskFactory(factory.Factory):
    class Meta:
        model = Task

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TaskState)
    user_id = 1


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
    pwd = 'senhateste'
    user = UserFactory(
        password=get_password_hash(pwd),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = pwd

    return user


@pytest.fixture
def user2(session):
    pwd = 'senhateste'
    user = UserFactory(
        password=get_password_hash(pwd),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = pwd

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_handler)

    yield time

    event.remove(model, 'before_insert', fake_time_handler)


@pytest.fixture
def mock_db_time():
    return _mock_db_time

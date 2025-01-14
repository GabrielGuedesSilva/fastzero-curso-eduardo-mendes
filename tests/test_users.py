from http import HTTPStatus

from fastzero.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'name user',
            'email': 'john@email.com',
            'password': '12345',
        },
    )  # Act

    assert response.status_code == HTTPStatus.CREATED  # Assert
    assert response.json() == {
        'id': 1,
        'username': 'name user',
        'email': 'john@email.com',
    }  # Assert


def test_create_user_username_already_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'test@email.com',
            'password': '12345',
        },
    )  # Act

    assert response.status_code == HTTPStatus.BAD_REQUEST  # Assert
    assert response.json() == {
        'detail': 'Username already exists',
    }  # Assert


def test_create_user_email_already_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'test user 2',
            'email': user.email,
            'password': '12345',
        },
    )  # Act

    assert response.status_code == HTTPStatus.BAD_REQUEST  # Assert
    assert response.json() == {
        'detail': 'Email already exists',
    }  # Assert


def test_get_users(client):
    response = client.get('/users/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'users': []}  # Assert


def test_get_users_with_users_registered(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'users': [user_schema]}  # Assert


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'TESTE UPDATE',
            'email': 'teste@email.com',
            'password': '12345',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'TESTE UPDATE',
        'email': 'teste@email.com',
    }


def test_get_user_by_id(client, user):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


def test_get_user_by_id_not_found(client):
    response = client.get('/users/3')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_update_wrong_user(client, user2, token):
    response = client.put(
        f'/users/{user2.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'TESTE UPDATE',
            'email': 'teste@email.com',
            'password': '12345',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_wrong_user(client, user2, token):
    response = client.delete(
        f'/users/{user2.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}

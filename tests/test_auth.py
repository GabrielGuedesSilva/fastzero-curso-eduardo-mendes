from http import HTTPStatus

from freezegun import freeze_time

from fastzero.security import create_access_token


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        # Passamos a variável data quando é formulário
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_token_sub_not_send(client):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_user_not_exists(client):
    data = {'sub': 'test@fake.com'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_not_decode(client):
    token = 'invalid-token'

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_login_incorret_email(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'wrong-email', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_login_incorret_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrongpassword'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_token_expired_after_time(client, user):
    with freeze_time('2021-01-01 12:00:00'):
        # Gerar o token (12:00)
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2021-01-01 12:31:00'):
        # Chamar uma função que depende do token (12:31)
        response = client.put(
            f'users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'test-username',
                'email': 'test-email',
                'password': 'test-password',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_token(client, token):
    response = client.post(
        '/auth/refresh/token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'
    assert 'access_token' in data


def test_token_expired_dont_refresh(client, user):
    with freeze_time('2021-01-01 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2021-01-01 12:31:00'):
        response = client.post(
            '/auth/refresh/token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}

from http import HTTPStatus


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'message': 'Hello World'}  # Assert


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


def test_get_users(client):
    response = client.get('/users/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'name user',
                'email': 'john@email.com',
            }
        ]
    }  # Assert


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'TESTE UPDATE',
            'email': 'teste@email.com',
            'password': '12345',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'TESTE UPDATE',
        'email': 'teste@email.com',
    }


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_update_user_not_found(client):
    response = client.put(
        '/users/2',
        json={
            'username': 'TESTE UPDATE',
            'email': 'teste@email.com',
            'password': '12345',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user_not_found(client):
    response = client.delete('/users/2')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}

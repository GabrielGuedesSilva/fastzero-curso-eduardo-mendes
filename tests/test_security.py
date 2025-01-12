from http import HTTPStatus

from jwt import decode

from fastzero.security import create_access_token
from fastzero.settings import Settings

settings = Settings()


def test_jwt():
    data = {'sub': 'test@test.com'}
    token = create_access_token(data)

    result = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert result['sub'] == data['sub']
    assert result['exp']


# Tentando fazr uma operação que necessita de autenticação, enviando um
# token inválido
def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Invalid bearer token'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}

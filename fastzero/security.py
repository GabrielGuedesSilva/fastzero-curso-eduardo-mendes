from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastzero.database import get_session
from fastzero.models import User
from fastzero.settings import Settings

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')
settings = Settings()


# Encriptação de senha
def get_password_hash(password):
    return pwd_context.hash(password)


# Verifica se a senha limpa e a senha encriptada são iguais
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# Criação do token
def create_access_token(data_payload: dict):
    to_encode = data_payload.copy()

    # Adicionando tempo de expiração ao token
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})

    # token = payload + secret_key + algoritmo de assinatura
    encoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


# Capturar usuário que está logado
async def get_current_user(
    session: Session = Depends(get_session),
    # Com essa depndência, qualquer usuário que for fazer essa operação
    # precisa estar logado
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get('sub')

        if not username:
            raise credentials_exception
    except ExpiredSignatureError:
        raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user = session.scalar(select(User).where(User.email == username))

    if not user:
        raise credentials_exception

    return user

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastzero.database import get_session
from fastzero.models import User
from fastzero.schemas import Token
from fastzero.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(
    # Prefixo para as rotas desse router
    prefix='/auth',
    # Parâmetro para organizar as rotas na documentação
    tags=['auth'],
)
T_Session = Annotated[Session, Depends(get_session)]
# Indica que o formulário auth form deve ser recebido
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
def login_for_access_token(session: T_Session, form_data: T_OAuth2Form):
    # Verificando existência do usuário e se a senha está correta
    user = session.scalar(select(User).where(User.email == form_data.username))
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data_payload={'sub': user.email})

    return {'token_type': 'Bearer', 'access_token': access_token}


@router.post('/refresh/token', response_model=Token)
def refresh_access_token(user: User = Depends(get_current_user)):
    new_access_token = create_access_token(data_payload={'sub': user.email})

    return {'token_type': 'Bearer', 'access_token': new_access_token}

from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastzero.routers import auth, tasks, users
from fastzero.schemas import Message

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tasks.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Permitir qualquer origem
    allow_credentials=True,
    allow_methods=['*'],  # Permitir todos os métodos
    allow_headers=['*'],  # Permitir todos os cabeçalhos
)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World'}

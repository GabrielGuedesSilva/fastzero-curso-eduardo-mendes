from http import HTTPStatus

from fastapi import FastAPI

from fastzero.routers import auth, tasks, users
from fastzero.schemas import Message

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World'}

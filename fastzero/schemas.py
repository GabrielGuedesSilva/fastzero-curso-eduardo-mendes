from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from fastzero.models import TaskState


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


# Schema para retorno público
class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    token_type: str  # modelo que o cliente deve usar para autorização
    access_token: str  # token jwt que será gerado


class TaskSchema(BaseModel):
    title: str
    description: str
    state: TaskState


class TaskPublic(TaskSchema):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class TaskList(BaseModel):
    tasks: list[TaskPublic]


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    state: TaskState | None = None

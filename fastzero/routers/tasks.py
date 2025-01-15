from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastzero.database import get_session
from fastzero.models import Task, User
from fastzero.schemas import TaskList, TaskPublic, TaskSchema, TaskUpdate
from fastzero.security import get_current_user

router = APIRouter(prefix='/tasks', tags=['tasks'])
T_Session = Annotated[Session, Depends(get_session)]
T_User = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TaskPublic)
def create_task(task: TaskSchema, session: T_Session, user: T_User):
    db_task = Task(
        title=task.title,
        description=task.description,
        state=task.state,
        user_id=user.id,
    )

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task


@router.get('/', response_model=TaskList)
def list_tasks(
    session: T_Session,
    user: T_User,
    title: str | None = None,
    description: str | None = None,
    state: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
):
    query = select(Task).where(Task.user_id == user.id)

    if title:
        query = query.where(Task.title.contains(title))

    if description:
        query = query.where(Task.description.contains(description))

    if state:
        query = query.where(Task.state == state)

    tasks = session.scalars(query.offset(offset).limit(limit)).all()

    return {'tasks': tasks}


@router.delete('/{task_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_task(task_id: int, session: T_Session, user: T_User):
    task = session.scalar(
        select(Task).where(Task.user_id == user.id, Task.id == task_id)
    )

    if not task:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    session.delete(task)
    session.commit()


@router.patch(
    '/{task_id}', status_code=HTTPStatus.OK, response_model=TaskPublic
)
def update_task(
    task_id: int, task: TaskUpdate, session: T_Session, user: T_User
):
    db_task = session.scalar(
        select(Task).where(Task.user_id == user.id, Task.id == task_id)
    )

    if not db_task:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task

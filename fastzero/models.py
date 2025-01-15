# Onde irão ficar os modelos do banco de dados
from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry

# registro de metadados
table_registry = registry()


class TaskState(str, Enum):
    TODO = 'todo'
    DOING = 'doing'
    DONE = 'done'
    DRAFT = 'draft'
    TRASH = 'trash'


# Mapeando um objeto para uma tabela do banco de dados
@table_registry.mapped_as_dataclass
class User:
    # Nome da tabela no bd
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )


@table_registry.mapped_as_dataclass
class Task:
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    state: Mapped[TaskState]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

from datetime import date, datetime
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, Date, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

app = FastAPI(title="Task Management API", version="1.0.0")
APP_PORT = 8080

DATABASE_PATH = Path(__file__).with_name("tasks.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String, nullable=False)
    contenido: Mapped[str] = mapped_column(String, nullable=False)
    deadline: Mapped[date] = mapped_column(Date, nullable=False)
    completada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


class TaskCreate(BaseModel):
    titulo: str = Field(min_length=1, description="Titulo de la tarea")
    contenido: str = Field(min_length=1, description="Contenido de la tarea")
    deadline: date = Field(description="Fecha de vencimiento")


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    contenido: str
    deadline: date
    completada: bool
    fecha_creacion: datetime


class TaskContentCleaner:
    def __init__(self) -> None:
        self._blocked_words = ["tonto", "feo", "malo"]

    def clean(self, content: str) -> str:
        cleaned_content = content
        for word in self._blocked_words:
            cleaned_content = cleaned_content.replace(word, "*" * len(word))
            cleaned_content = cleaned_content.replace(word.capitalize(), "*" * len(word))
        return cleaned_content.strip()


class TaskDeadlineChecker:
    def is_expired(self, deadline: date) -> bool:
        return deadline < date.today()


class TaskManager:
    def __init__(self) -> None:
        self._cleaner = TaskContentCleaner()
        self._deadline_checker = TaskDeadlineChecker()

    def _get_session(self) -> Session:
        return SessionLocal()

    def create_task(self, task_data: TaskCreate) -> TaskResponse:
        cleaned_content = self._cleaner.clean(task_data.contenido)
        task = Task(
            titulo=task_data.titulo.strip(),
            contenido=cleaned_content,
            deadline=task_data.deadline,
            completada=False,
            fecha_creacion=datetime.now(),
        )

        session = self._get_session()
        session.add(task)
        session.commit()
        session.refresh(task)
        response = TaskResponse.model_validate(task)
        session.close()
        return response

    def get_task(self, task_id: int) -> TaskResponse:
        session = self._get_session()
        task = session.get(Task, task_id)
        if task is None:
            session.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada",
            )
        response = TaskResponse.model_validate(task)
        session.close()
        return response

    def complete_task(self, task_id: int) -> TaskResponse:
        session = self._get_session()
        task = session.get(Task, task_id)
        if task is None:
            session.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada",
            )
        task.completada = True
        session.commit()
        session.refresh(task)
        response = TaskResponse.model_validate(task)
        session.close()
        return response

    def get_expired_tasks(self) -> List[TaskResponse]:
        session = self._get_session()
        tasks = session.query(Task).order_by(Task.id).all()
        expired_tasks = []
        for task in tasks:
            if self._deadline_checker.is_expired(task.deadline):
                expired_tasks.append(TaskResponse.model_validate(task))
        session.close()
        return expired_tasks

    def get_all_tasks(self) -> List[TaskResponse]:
        session = self._get_session()
        tasks = session.query(Task).order_by(Task.id).all()
        response = [TaskResponse.model_validate(task) for task in tasks]
        session.close()
        return response

    def delete_task(self, task_id: int) -> None:
        session = self._get_session()
        task = session.get(Task, task_id)
        if task is None:
            session.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada",
            )
        session.delete(task)
        session.commit()
        session.close()


task_manager = TaskManager()


@app.get("/")
def root():
    return {"message": "Task Management API"}


@app.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(task: TaskCreate):
    return task_manager.create_task(task)


@app.get("/tasks/", response_model=List[TaskResponse])
def obtener_tareas():
    return task_manager.get_all_tasks()


@app.get("/tasks/caducadas", response_model=List[TaskResponse])
def obtener_tareas_caducadas():
    return task_manager.get_expired_tasks()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def obtener_tarea(task_id: int):
    return task_manager.get_task(task_id)


@app.put("/tasks/{task_id}/completar", response_model=TaskResponse)
def marcar_completada(task_id: int):
    return task_manager.complete_task(task_id)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_tarea(task_id: int):
    task_manager.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=APP_PORT, reload=True)

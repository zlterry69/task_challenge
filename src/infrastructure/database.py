import os
from datetime import datetime
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from src.domain.entities import TaskPriority, TaskStatus

try:
    load_dotenv()
except Exception:
    pass

Base = declarative_base()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://taskuser:taskpass123@localhost:3307/task_db"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owned_task_lists = relationship("TaskListModel", back_populates="owner")
    assigned_tasks = relationship("TaskModel", back_populates="assignee")


class TaskListModel(Base):
    __tablename__ = "task_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("UserModel", back_populates="owned_task_lists")
    tasks = relationship(
        "TaskModel", back_populates="task_list", cascade="all, delete-orphan"
    )


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    task_list_id = Column(Integer, ForeignKey("task_lists.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)

    task_list = relationship("TaskListModel", back_populates="tasks")
    assignee = relationship("UserModel", back_populates="assigned_tasks")


class DatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        if "mysql+pymysql" in database_url:
            self.async_database_url = database_url.replace(
                "mysql+pymysql", "mysql+aiomysql"
            )
        else:
            self.async_database_url = database_url

        self.engine = create_async_engine(
            self.async_database_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        self.async_session_maker = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self):
        await self.engine.dispose()


database_manager: DatabaseManager = None


def get_database_manager() -> DatabaseManager:
    global database_manager
    if database_manager is None:
        raise RuntimeError("Database manager not initialized")
    return database_manager


def init_database(database_url: str) -> DatabaseManager:
    global database_manager
    database_manager = DatabaseManager(database_url)
    return database_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db_manager = get_database_manager()
    async for session in db_manager.get_session():
        yield session

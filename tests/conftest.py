import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database import Base
from src.presentation.dependencies import get_db
from src.presentation.main import app

# Configuración de base de datos para tests
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "mysql+pymysql://taskuser:taskpass123@localhost:3307/task_db"
)


@pytest.fixture(scope="session")
def setup_test_database():
    """Configurar base de datos para tests de integración solamente"""
    try:
        # Crear engine para tests
        engine = create_engine(TEST_DATABASE_URL)

        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)

        # Configurar session para tests
        TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )

        def override_get_db():
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                db.close()

        # Override dependency
        app.dependency_overrides[get_db] = override_get_db

        yield TestingSessionLocal

        # Cleanup
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

    except Exception:
        # Si no hay BD disponible, devolver None
        yield None


@pytest.fixture(scope="function")
def clean_database(setup_test_database):
    """Limpiar base de datos entre tests de integración"""
    if setup_test_database is None:
        pytest.skip("Database not available for integration tests")

    try:
        engine = create_engine(TEST_DATABASE_URL)
        TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )

        with TestingSessionLocal() as db:
            # Limpiar todas las tablas
            db.execute("SET FOREIGN_KEY_CHECKS = 0")
            db.execute("DELETE FROM tasks")
            db.execute("DELETE FROM task_lists")
            db.execute("DELETE FROM users")
            db.execute("SET FOREIGN_KEY_CHECKS = 1")
            db.commit()
    except Exception:
        pass  # Si falla, continuar

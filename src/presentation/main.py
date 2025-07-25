import os
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from src.infrastructure.database import init_database
from src.presentation.graphql.schema import schema
from src.presentation.routers.auth import router as auth_router
from src.presentation.routers.task_lists import router as task_list_router
from src.presentation.routers.tasks import router as task_router

app = FastAPI(
    title="Task Challenge API",
    description="REST and GraphQL API for task management with Clean Architecture",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    database_url = os.getenv(
        "DATABASE_URL", "mysql+pymysql://taskuser:taskpass123@localhost:3306/task_db"
    )
    init_database(database_url)
    print(f"✅ Database manager initialized with URL: {database_url}")

# GraphQL router simple
graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql", include_in_schema=True)

# REST routers
app.include_router(auth_router)
app.include_router(task_list_router)
app.include_router(task_router)

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/")
def root():
    return {
        "message": "Task Challenge API",
        "docs": "/docs",
        "graphql": "/graphql",
        "health": "/ping",
    }

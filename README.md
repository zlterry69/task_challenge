# Task Challenge API

API REST y GraphQL para gestión de listas de tareas desarrollada con FastAPI, Strawberry GraphQL y arquitectura limpia por capas.

---

## Descripción del Proyecto

Este proyecto implementa una API dual (REST + GraphQL) para la gestión de listas de tareas con las siguientes características:

### Funcionalidades Implementadas
- CRUD completo de listas de tareas (REST y GraphQL)
- CRUD completo de tareas con estados y prioridades (REST y GraphQL)
- Sistema de autenticación JWT (funciona en ambas APIs)
- Asignación de usuarios a tareas con notificaciones por email (ficticio)
- Cálculo de porcentaje de completitud automático
- Determinación de tareas vencidas (`is_overdue`)
- Filtros avanzados por estado, prioridad, fecha límite
- Validación completa con Pydantic y Strawberry
- Testing completo (81% cobertura + tests de integración)

### APIs Disponibles
- **REST API**: Endpoints tradicionales con FastAPI + Swagger UI
- **GraphQL API**: Queries y mutations con Strawberry + GraphQL Playground
- **Documentación automática**: OpenAPI 3.0 y GraphQL introspection

---

## Arquitectura

Arquitectura limpia por capas con separación clara de responsabilidades:

```
src/
├── domain/              
│   ├── entities.py      
│   └── exceptions.py    
├── application/         
│   ├── services.py      
│   ├── auth_service.py  
│   ├── dto.py           
│   └── notifications.py 
├── infrastructure/     
│   ├── database.py      
│   ├── repositories.py  
│   └── auth.py          
└── presentation/       
    ├── main.py          
    ├── dependencies.py  
    ├── routers/         
    │   ├── auth.py      
    │   ├── tasks.py     
    │   └── task_lists.py 
    └── graphql/         
        ├── schema.py    
        ├── types.py     
        └── resolvers/   
            ├── auth_resolvers.py
            ├── task_resolvers.py
            └── task_list_resolvers.py
```

---

## Stack Tecnológico

- **Python 3.12+** - Lenguaje base
- **FastAPI** - Framework web moderno y rápido
- **Strawberry GraphQL** - GraphQL server moderno para Python
- **MySQL 8.0** - Base de datos principal
- **SQLAlchemy** - ORM con soporte async
- **Pydantic v2** - Validación de datos REST
- **JWT** (JSON Web Tokens) - Autenticación stateless
- **pytest** - Framework de testing (81% cobertura)
- **Docker** - Containerización
- **Redis** - Caching (preparado para futuro)

---

## Configuración del Entorno

### Prerrequisitos
- **Python 3.12+**
- **Docker & Docker Compose**
- **Git**

### Instalación Rápida

1. **Clonar repositorio**
   ```bash
   git clone <repository-url>
   cd task_challenge
   ```

2. **Opción A: Docker (Recomendado)**
   ```bash
   docker-compose up --build
   ```
   
3. **Opción B: Desarrollo local**
   ```bash
   python -m venv venv
   source venv/bin/activate  
   
   pip install -r requirements.txt
   
   cp .env.example .env
   
   uvicorn src.presentation.main:app --reload
   ```

### URLs Disponibles
- **API REST**: http://localhost:8000
- **GraphQL**: http://localhost:8000/graphql
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## API REST Endpoints

### Autenticación
```
POST /api/auth/register     
POST /api/auth/login        
GET  /api/auth/me          
```

### Listas de Tareas
```
GET    /api/task-lists/           
POST   /api/task-lists/           
GET    /api/task-lists/{id}       
PUT    /api/task-lists/{id}       
DELETE /api/task-lists/{id}       
```

### Tareas
```
GET    /api/tasks/                
POST   /api/tasks/                
PUT    /api/tasks/{id}            
DELETE /api/tasks/{id}            
PATCH  /api/tasks/{id}/status     
GET    /api/tasks/stats           
```

---

## GraphQL API

### Endpoint
- **Endpoint**: `POST /graphql`
- **Playground**: `GET /graphql` (interfaz interactiva)

### Queries Principales

```graphql
query GetTaskLists {
  taskLists {
    id
    name
    description
    completionPercentage
    taskCount
  }
}

query GetTasks($filter: TaskFilterInput) {
  tasks(filter: $filter) {
    id
    title
    status
    priority
    isOverdue
    assigneeName
    dueDate
  }
}
```

### Mutations Principales

```graphql
mutation CreateTaskList($input: TaskListCreateInput!) {
  createTaskList(input: $input) {
    id
    name
    description
  }
}

mutation CreateTask($input: TaskCreateInput!) {
  createTask(input: $input) {
    id
    title
    status
    priority
  }
}
```

---

## Testing

### Cobertura Actual: 81%

```bash
pytest

pytest --cov=src --cov-report=term-missing

pytest tests/unit/ -v

pytest tests/integration/ -v
```

### Estructura de Testing

```
tests/
├── unit/                          
│   ├── test_auth.py              
│   ├── test_domain.py            
│   ├── test_application_services.py  
│   ├── test_infrastructure.py    
│   ├── test_task_resolvers_deep.py   
│   ├── test_task_list_resolvers_deep.py 
│   └── test_validation_and_security.py 
└── integration/                   
    ├── test_auth_integration.py  
    ├── test_graphql_integration.py 
    ├── test_task_lists_integration.py 
    └── test_tasks_integration.py 
```

---

## Ejemplos de Uso

### REST API

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

curl -X POST http://localhost:8000/api/task-lists/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Mi Lista", "description": "Mi primera lista"}'
```

### GraphQL

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ taskLists { id name completionPercentage } }"
  }'
```

---

## Variables de Entorno

```env
DATABASE_URL=mysql+pymysql://taskuser:taskpass123@localhost:3307/task_db

SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

DEBUG=true
```

---

## Comandos Útiles

### Desarrollo
```bash
uvicorn src.presentation.main:app --reload

pytest --cov=src --cov-report=html

black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

### Docker
```bash
docker-compose up --build

docker-compose down
```

### Base de Datos (Alembic)
```bash
alembic revision --autogenerate -m "Descripción del cambio"

alembic upgrade head
```

---

## Contribución

1. **Fork** del proyecto
2. **Crear rama** para feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Implementar** con tests
4. **Verificar calidad** (`make lint && pytest`)
5. **Commit** cambios (`git commit -am 'Add nueva funcionalidad'`)
6. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
7. **Crear Pull Request**

---

## Documentación Adicional

- **DECISION_LOG.md**: Decisiones técnicas detalladas y justificaciones
- **Swagger UI**: Documentación interactiva REST en `/docs`
- **GraphQL Playground**: Exploración de schema en `/graphql`

---

## Licencia

MIT License - Ver archivo `LICENSE` para detalles completos.
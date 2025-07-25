# Decision Log - Task Challenge API

Este documento registra las principales decisiones técnicas tomadas durante el desarrollo del proyecto.

---

## Arquitectura General

### ✅ Arquitectura por Capas (Clean Architecture)

**Decisión:** Implementar arquitectura limpia con separación en capas Domain, Application, Infrastructure y Presentation.

**Justificación:**
- **Mantenibilidad:** Facilita el mantenimiento y evolución del código
- **Testabilidad:** Permite testing unitario efectivo al aislar dependencias (81% cobertura alcanzada)
- **Flexibilidad:** Facilita cambios en tecnologías específicas sin afectar la lógica de negocio
- **Escalabilidad:** Estructura clara para equipos grandes

**Alternativas consideradas:**
- Patrón MVC tradicional
- Arquitectura monolítica simple

---

## API Design

### ✅ FastAPI + Strawberry GraphQL - API Dual

**Decisión:** Implementar tanto REST como GraphQL usando FastAPI y Strawberry GraphQL.

**Justificación:**
- **Flexibilidad total:** REST para operaciones simples, GraphQL para consultas complejas
- **Documentación automática:** FastAPI genera Swagger, GraphQL tiene introspección
- **Performance:** FastAPI + Strawberry ofrecen excelente rendimiento
- **Tipado fuerte:** Excelente soporte para type hints en ambas APIs
- **Buenas prácticas GraphQL:** Separación de concerns, tipos diferenciados, optimización de queries

**Alternativas consideradas:**
- Solo REST (menos flexible para consultas complejas)
- Solo GraphQL (más complejo para operaciones CRUD simples)
- Otros frameworks GraphQL (Ariadne, Graphene)

---

## Base de Datos

### ✅ MySQL + SQLAlchemy

**Decisión:** Usar MySQL como base de datos principal con SQLAlchemy como ORM.

**Justificación:**
- **Robustez:** MySQL es altamente confiable para aplicaciones de producción
- **Disponibilidad:** Fácil configuración en Docker para desarrollo
- **SQLAlchemy:** ORM maduro con excelente soporte para migraciones (Alembic)
- **Tipado:** Integración natural con Pydantic para validaciones
- **GraphQL friendly:** SQLAlchemy facilita resolvers eficientes

**Alternativas consideradas:**
- PostgreSQL (excelente opción, pero MySQL más familiar)
- SQLite (descartado por limitaciones en producción)
- MongoDB (descartado por naturaleza relacional de los datos)

### ✅ Migraciones con Alembic

**Decisión:** Usar Alembic para manejo de migraciones de base de datos.

**Justificación:**
- **Versionado:** Control de versiones de esquema de BD
- **Rollback:** Capacidad de revertir cambios
- **Colaboración:** Facilita trabajo en equipo
- **Automatización:** Integrable en pipelines CI/CD

---

## Autenticación y Autorización

### ✅ JWT (JSON Web Tokens)

**Decisión:** Implementar autenticación basada en JWT que funcione en REST y GraphQL.

**Justificación:**
- **Stateless:** No requiere almacenamiento de sesiones en servidor
- **Escalabilidad:** Ideal para APIs REST y GraphQL
- **Estándar:** Ampliamente adoptado en la industria
- **Flexibilidad:** Permite incluir claims personalizados
- **GraphQL compatible:** Fácil implementación en headers HTTP

**Alternativas consideradas:**
- Sesiones basadas en cookies (problemático para GraphQL)
- OAuth 2.0 (descartado por complejidad para el scope actual)

### ✅ Bcrypt para Hash de Passwords

**Decisión:** Usar bcrypt para hashear contraseñas.

**Justificación:**
- **Seguridad:** Algoritmo probado y seguro
- **Salt automático:** Protección contra rainbow tables
- **Configurabilidad:** Permite ajustar factor de trabajo
- **Soporte:** Amplio soporte en Python

---

## Validación y Serialización

### ✅ Pydantic v2 + Strawberry Types

**Decisión:** Usar Pydantic para validación REST y tipos Strawberry para GraphQL.

**Justificación:**
- **Pydantic:** Perfecto para REST API con FastAPI
- **Strawberry:** Tipos nativos GraphQL con validación automática
- **Interoperabilidad:** Ambos sistemas se complementan
- **Performance:** Pydantic v2 es significativamente más rápido
- **Tipado fuerte:** Integración natural con type hints de Python
- **Documentación:** Genera automáticamente documentación OpenAPI y GraphQL schema

**Alternativas consideradas:**
- Marshmallow (descartado por performance y integración)
- Validación manual (descartado por mantenibilidad)

---

## Testing

### ✅ pytest + pytest-asyncio

**Decisión:** Usar pytest como framework principal con tests específicos para cada API.

**Justificación:**
- **Flexibilidad:** Soporta múltiples estilos de testing
- **Fixtures:** Sistema potente de fixtures para setup/teardown
- **Plugins:** Ecosistema rico de plugins
- **GraphQL testing:** TestClient de FastAPI funciona perfectamente con GraphQL
- **Async support:** Excelente soporte para testing asíncrono

### ✅ Separación de Tests Unitarios e Integración

**Decisión:** Separar tests unitarios de tests de integración en directorios diferentes.

**Justificación:**
- **Velocidad:** Tests unitarios son más rápidos (722 tests unitarios)
- **Feedback:** Permite ejecutar solo tests rápidos durante desarrollo
- **CI/CD:** Facilita configuración de pipelines con diferentes etapas
- **GraphQL específico:** Tests de introspección, queries complejas, error handling

### ✅ Tests contra Base de Datos Real

**Decisión:** Usar base de datos real MySQL para tests de integración.

**Justificación:**
- **Realismo:** Tests contra base de datos real
- **Confiabilidad:** Detecta problemas que mocks no pueden encontrar
- **GraphQL testing:** Validación completa de queries complejas

---

## Linting y Formateo

### ✅ Black + isort + flake8

**Decisión:** Usar combinación de Black, isort y flake8 para formateo y linting.

**Justificación:**
- **Black:** Formateo automático sin configuración
- **isort:** Organización automática de imports
- **flake8:** Detección de problemas de código y estilo
- **Integración:** Herramientas complementarias, no conflictivas
- **GraphQL friendly:** Configuración que no interfiere con strings GraphQL largos

**Configuración:**
- Black: line-length 88 (default)
- isort: perfil compatible con Black
- flake8: ignorar reglas conflictivas con Black

---

## Containerización

### ✅ Docker Multi-stage Build

**Decisión:** Implementar Dockerfile con multi-stage build optimizado.

**Justificación:**
- **Tamaño:** Imágenes más pequeñas para producción
- **Seguridad:** Imagen final sin herramientas de desarrollo
- **Separación:** Diferentes etapas para dev y prod
- **Performance:** Builds más rápidos con caching de layers

### ✅ Docker Compose para Desarrollo

**Decisión:** Incluir docker-compose.yml para facilitar desarrollo local.

**Justificación:**
- **Simplicidad:** Un comando para levantar todo el stack
- **Consistencia:** Mismo entorno para todos los desarrolladores
- **Servicios:** Incluye MySQL, Redis y healthchecks
- **Desarrollo:** Hot-reload y mounting de código

---

## Manejo de Errores

### ✅ Errores Diferenciados REST vs GraphQL

**Decisión:** Crear sistemas de error apropiados para cada tipo de API.

**Justificación:**
- **REST:** HTTP status codes apropiados
- **GraphQL:** Errores en response payload siguiendo spec GraphQL
- **Consistency:** Errores consistentes pero apropiados para cada API
- **Debugging:** Información específica para cada tipo de cliente

### ✅ Excepciones Personalizadas por Dominio

**Decisión:** Crear jerarquía de excepciones específicas del dominio.

**Justificación:**
- **Claridad:** Errores específicos del dominio de tareas
- **Manejo centralizado:** Exception handlers globales
- **Debugging:** Información más específica para debugging

---

## Performance

### ✅ Optimizaciones GraphQL

**Decisión:** Implementar buenas prácticas de performance en GraphQL.

**Justificación:**
- **N+1 Problem:** Resolvers optimizados para evitar múltiples queries
- **Efficient resolvers:** Queries agrupadas cuando es posible
- **Field resolution:** Solo campos solicitados son procesados

### ✅ Database Optimization

**Decisión:** Optimizar queries de base de datos para ambas APIs.

**Justificación:**
- **Eager loading:** Relaciones cargadas eficientemente
- **Query optimization:** Sin N+1 problems en GraphQL
- **Connection pooling:** SQLAlchemy configurado para alta concurrencia

---

## Features Implementadas

### ✅ Sistema de Notificaciones (Fictitious)

**Decisión:** Implementar simulación de notificaciones por email.

**Justificación:**
- **Task assignment:** Email automático al asignar tarea
- **Task completion:** Notificación al owner cuando se completa
- **Configurable:** Puede deshabilitarse con variable de entorno
- **Extensible:** Estructura preparada para notificaciones reales

### ✅ Cálculo Automático de Métricas

**Decisión:** Implementar cálculo automático de estadísticas y métricas.

**Justificación:**
- **Completion percentage:** Porcentaje automático por lista
- **Overdue detection:** Identificación automática de tareas vencidas
- **Task counting:** Conteo dinámico de tareas por estado
- **Performance:** Cálculos eficientes sin impacto en rendimiento

---

## Configuración

### ✅ Variables de Entorno con Validación

**Decisión:** Usar variables de entorno con validación para configuración.

**Justificación:**
- **Flexibilidad:** Configuración diferente por ambiente
- **Seguridad:** Secrets no hardcodeados en código
- **Validación:** Verificación automática de configuración requerida
- **Docker friendly:** Fácil configuración en contenedores

---

## Decisiones Pendientes / Futuras Consideraciones

### 🔄 Cache Layer

**Consideración futura:** Implementar caching con Redis para queries GraphQL frecuentes.

**Justificación:** Para mejorar performance en consultas complejas y repetitivas.

### 🔄 Rate Limiting

**Consideración futura:** Implementar rate limiting diferenciado por API.

**Justificación:** GraphQL puede ser más costoso que REST endpoints simples.

### 🔄 Observabilidad

**Consideración futura:** Implementar métricas específicas para GraphQL.

**Justificación:** Monitoring de performance de queries vs mutations.

### 🔄 GraphQL Subscriptions

**Consideración futura:** Implementar subscriptions para updates en tiempo real.

**Justificación:** Notificaciones push cuando cambian estados de tareas.

### 🔄 DataLoader Pattern

**Consideración futura:** Implementar DataLoaders para optimización de queries.

**Justificación:** Solución definitiva al problema N+1 en GraphQL. 
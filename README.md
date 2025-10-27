# Payments Conversational Agent

Agente conversacional transaccional construido con FastAPI y LangChain que guía a los usuarios durante el envío de dinero usando lenguaje natural. Incluye integración resiliente con un servicio externo de pagos (mock), persistencia en PostgreSQL, migraciones Alembic y pruebas automatizadas.

## Tabla de contenido
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Configuración local](#configuración-local)
- [Ejecución de pruebas](#ejecución-de-pruebas)
- [Ejecución con Docker](#ejecución-con-docker)
- [Migraciones](#migraciones)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Decisiones clave](#decisiones-clave)

## Arquitectura
- **FastAPI** expone los endpoints REST del agente.
- **LangChain** orquesta las respuestas conversacionales mediante un prompt controlado y un modelo configurable (OpenAI o modo determinista).
- **PostgreSQL** almacena conversaciones y transacciones; SQLAlchemy gestiona el acceso.
- **Cliente HTTP resiliente** consume la API de pagos mock con retry, timeout y circuit breaker.
- **Docker Compose** levanta los servicios `app`, `db` y `mock-api`.

## Requisitos
- Python 3.12+
- PostgreSQL 14+
- Docker y Docker Compose (opcional para despliegue contenedorizado)

## Configuración local
1. Crear y activar un entorno virtual.
2. Instalar dependencias:
   ```bash
   pip install -e .
   pip install -e .[test]
   ```
3. Copiar variables de entorno:
   ```bash
   cp .env.example .env
   ```
   Ajusta `DATABASE_URL` y `OPENAI_API_KEY` según tu entorno.
4. Ejecutar migraciones:
   ```bash
   alembic upgrade head
   ```
5. Iniciar la API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Ejecución de pruebas
```bash
pytest
```
Genera reporte de cobertura (mínimo 70%).

## Ejecución con Docker
```bash
docker-compose up --build
```
La API quedará disponible en `http://localhost:8000`, el servicio mock en `http://localhost:8001`.

## Migraciones
- Archivo de configuración: `alembic.ini`
- Script inicial: `alembic/versions/202405130001_create_tables.py`
- Ejecutar `alembic upgrade head` para aplicar los cambios.

## Estructura del proyecto
```
app/
  agent/                Lógica del agente y herramientas LangChain
  api/                  Rutas FastAPI
  clients/              Cliente HTTP con resiliencia
  core/                 Configuración y logging
  db/                   Sesiones y base declarativa
  models/               Modelos ORM
  schemas/              Esquemas Pydantic
  services/             Casos de uso y reglas de negocio
  utils/                Utilidades de parsing
mock_api/               Servicio mock de pagos
alembic/                Migraciones
Dockerfile              Imagen principal de la app
mock_api/Dockerfile     Imagen del mock
PROMPTS.md              Registro de prompts usados con IA
```

## Decisiones clave
- **Modo determinista por defecto**: `USE_FAKE_LLM=true` habilita un modelo de eco controlado para pruebas y entornos sin clave de OpenAI.
- **Resiliencia personalizada**: Se implementó un circuit breaker propio para cumplir con los tiempos de apertura/half-open solicitados, además de reintentos exponenciales con Tenacity.
- **Persistencia del contexto**: Las conversaciones guardan mensajes y estado en JSON para reconstruir el historial desde la API.
- **Pruebas mixtas**: Se cubren utilidades, cliente HTTP, flujo conversacional y endpoints, utilizando SQLite en memoria para aislar el entorno de test.

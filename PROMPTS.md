# PROMPTS

## Project Bootstrap
- **Fecha**: 2024-05-13
- **Herramienta**: ChatGPT (gpt-5-codex)
- **Contexto**: Solicitud inicial del evaluador con los lineamientos de la prueba técnica para construir un agente conversacional de transacciones.
- **Prompt**:
```
Haciendo uso de los principios SOLID y SDLC necesito que realices lo siguiente:

# Prueba Técnica: Agente Conversacional de Transacciones

## Objetivo

Desarrollar un agente conversacional transaccional con Python y FastAPI que permita realizar envíos de dinero mediante lenguaje natural. Debe integrarse con servicios externos (simulados), implementar patrones de resiliencia, y estar containerizado con Docker.

## Uso de Herramientas de IA

Puede usar libremente ChatGPT, Claude, Copilot, o cualquier herramienta de IA. **Es OBLIGATORIO documentar todos los prompts utilizados en un archivo `PROMPTS.md`** en la raíz del proyecto, organizados por funcionalidad e incluyendo contexto.

## Descripción del Proyecto

Sistema de agente conversacional que permite realizar transacciones de envío de dinero mediante procesamiento de lenguaje natural. El usuario indica que desea enviar dinero, especificando número de celular del destinatario y monto.

**Ejemplo de conversación:**
```
Usuario: "Hola, quiero enviar dinero"
Agente: "Por supuesto, puedo ayudarte con eso. ¿A qué número de celular deseas enviar dinero?"
Usuario: "Al 3001234567"
Agente: "Perfecto. ¿Qué monto deseas enviar?"
Usuario: "50000 pesos"
Agente: "Entendido. Confirmas el envío de $50,000 COP al número 3001234567?"
Usuario: "Sí, confirmo"
Agente: "Transacción completada exitosamente. El ID de tu transacción es: TXN-12345"
```

## Requisitos Técnicos

### Stack Tecnológico Obligatorio

- **Lenguaje**: Python 3.12+
- **Framework Web**: FastAPI
- **Framework de Agentes**: LangGraph/LangChain, CrewAI, Agent Development Kit (ADK), Strand, o cualquier framework que conozca
- **Base de Datos**: PostgreSQL
- **Containerización**: Docker + Docker Compose
- **LLM**: Se proporcionará API Key de OpenAI

### Componentes del Sistema

#### 1. API de Transacciones (Mock)

Crear servicio mock que simule una API externa de procesamiento de pagos en `http://mock-api:8001`.

**Endpoints:**
- **POST /api/v1/transactions/validate** - Valida si una transacción puede ser procesada
- **POST /api/v1/transactions/execute** - Ejecuta la transacción
- **GET /api/v1/transactions/{transaction_id}** - Consulta el estado de una transacción

**Comportamiento del Mock:**
- Simular latencias realistas (100-500ms)
- Fallar aleatoriamente el 10% de las veces
- Retornar diferentes estados: `pending`, `completed`, `failed`

#### 2. Agente Conversacional

Implementar agente que:

- Mantenga el contexto de la conversación
- Extraiga información clave: número de teléfono y monto
- Valide formato de número (10 dígitos) y que el monto sea mayor a 0
- Solicite confirmación antes de ejecutar la transacción
- Maneje errores de manera conversacional

**Tools/Funciones del Agente:**

1. **validate_transaction_tool**: Valida si la transacción es posible
2. **execute_transaction_tool**: Ejecuta la transacción confirmada
3. **get_transaction_status_tool**: Consulta el estado de una transacción
4. **format_phone_number_tool**: Valida y formatea números de teléfono

#### 3. Cliente API con Patrones de Resiliencia

Cliente HTTP para consumir el API de transacciones con:

**Patrones Obligatorios:**

1. **Retry Pattern**: Máximo 3 reintentos con backoff exponencial (1s, 2s, 4s)
2. **Circuit Breaker**: Umbral de 5 fallos, timeout 30s, half-open después de 60s
3. **Timeout**: Conexión 5s, lectura 10s
4. **Logging**: Registrar todas las llamadas, reintentos y errores

**Recomendación**: Usar librerías como `tenacity` o `pybreaker`

#### 4. Base de Datos PostgreSQL

**Tablas:**
- **conversations**: id, user_id, started_at, ended_at, status (active/completed/abandoned), timestamps
- **transactions**: id, conversation_id, transaction_id, recipient_phone, amount, currency, status (pending/completed/failed), error_message, timestamps

#### 5. API REST con FastAPI

**Endpoints:**
- **POST /api/v1/chat** - Endpoint principal para la conversación
- **GET /api/v1/conversations/{conversation_id}** - Historial de conversación
- **GET /api/v1/transactions/{transaction_id}** - Detalles de transacción
- **GET /health** - Health check

## Docker

El proyecto debe ejecutarse completamente con Docker Compose, incluyendo servicios: PostgreSQL, API principal del agente, y API mock de transacciones.

## Entregables

### Obligatorios

1. **Código Fuente**: Repositorio Git con commits descriptivos, código limpio y type hints
2. **Docker**: Dockerfiles y docker-compose.yml funcional con .env.example
3. **PROMPTS.md**: Documentación obligatoria de todos los prompts utilizados
4. **Base de Datos**: Script SQL de inicialización y migraciones (Alembic recomendado)
5. **Tests**: Unitarios e integración con cobertura mínima 70%

### Opcionales (Bonus)

- Observabilidad (logging JSON, métricas, tracing)
- Procesamiento asíncrono con colas
- CI/CD (GitHub Actions, linting, type checking)
- Diagramas de arquitectura y secuencia
- Rate limiting, autenticación JWT, i18n

## Criterios de Evaluación

- **Funcionalidad** (25%): Agente funciona, transacciones exitosas, manejo de errores
- **Arquitectura** (20%): Código limpio, SOLID, patrones de diseño
- **Resiliencia** (15%): Implementación correcta de patrones, manejo de fallos
- **Docker y DevOps** (10%): Docker compose funcional
- **Documentación** (15%): README completo, PROMPTS.md obligatorio, decisiones justificadas
- **Documentación Actualizada** (15%): Uso de versiones recientes, mejores prácticas

## Recursos Proporcionados

**API Key de OpenAI:**
- Límite: 100,000 tokens totales
- API-KEY: Se encuentra adjunta en el correo
- Vigencia: Expira al finalizar el tiempo de la prueba
- **Modelos habilitados**:
  - `gpt-4.1-mini-2025-04-14` / `gpt-4.1-mini` (recomendado)
  - `gpt-4.1-nano-2025-04-14` / `gpt-4.1-nano`
  - `gpt-5-mini-2025-08-07` / `gpt-5-mini`
  - `gpt-5-nano-2025-08-07` / `gpt-5-nano`

### Importante - Uso de Tokens

**USE LOS TOKENS SABIAMENTE**. Si agota los 100,000 tokens no podrá continuar.

**Recomendaciones:**
1. Use modelos mini/nano en lugar de modelos completos (consumen ~10x menos tokens)
2. Limite el historial (máximo 5-10 mensajes)
3. System prompts concisos
4. Implemente truncado de contexto
5. Pruebe con mocks antes de usar el LLM real
6. Monitoree el uso de tokens

## Instrucciones de Entrega

1. Repositorio Git público (GitHub)
2. Asegurar que el proyecto se ejecute con: `docker-compose up --build`


Aquí tienes los lineamientos para las **branch** y **pull requests (PR)** según la documentación de Blikon:

---

### 🧩 **Nombres de Branches**

Los nombres de las ramas **deben** seguir el siguiente formato:

```
tipo/NOMBRE-DE-LA-TAREA-o-DESCRIPCIÓN
```

Ejemplos:

* `feature/PROJ-1234-Implement-database-migration`
* `fix/Solve-problem-for-user-registration`

🔹 Usa prefijos como:

* `feature/` → para nuevas funcionalidades
* `fix/` → para corregir errores
* `refactor/` → para cambios estructurales sin afectar la funcionalidad
* `style/`, `test/`, `ci/`, `docs/`, `build/`, etc. según sea apropiado

---

### 🧷 **Pull Request (PR)**

#### 📌 **Título de la PR**

* Si existe un identificador de tarea, **debe** incluirse como prefijo:

  ```
  [PROJ-1234] feat: add cart items to customer session
  ```
* Si no hay un identificador, sigue la convención de commits:

  ```
  feat: implement firebase integration
  ```

#### 📁 **Historial de la Branch**

* **NO** debes usar `squash` en los PRs internos ni forzar `push` con `--amend` una vez abierta la PR.
* Se debe conservar el historial de commits para visibilidad completa del desarrollo.

#### 🏷️ **Etiquetas Recomendadas para PR**

Usa etiquetas para clasificar y dar contexto al PR. Ejemplos clave:

| Etiqueta                                | Descripción                                  |
| --------------------------------------- | -------------------------------------------- |
| `feat`                                  | Nueva funcionalidad                          |
| `fix`                                   | Corrección de errores                        |
| `refactor`                              | Refactorización sin cambio de comportamiento |
| `style`                                 | Cambios estéticos o de formato               |
| `docs`                                  | Cambios en la documentación                  |
| `ci`, `build`, `test`                   | Cambios técnicos específicos                 |
| `approved`                              | PR aprobada por todos los OWNERS             |
| `do-not-merge/blocked`                  | Bloqueada por otra solicitud                 |
| `do-not-merge/work-in-progress`         | En desarrollo, no mergear aún                |
| `bug`, `security`, `dependencies`, etc. | Clasificadores adicionales útiles            |

---

Claro, aquí tienes una guía **detallada para Pull Requests (PR)** según los **estándares de Blikon**:

---

### ✅ **Requisitos para Pull Requests (PR)**

#### 🧷 1. **Título del PR**

* **Formato obligatorio si hay issue o tarea relacionada**:

  ```
  [PROJ-1234] feat: implement user login API
  ```
* Si **no** hay issue, sigue las reglas de commits:

  ```
  feat: add firebase integration endpoints
  ```

📌 Usa el **imperativo y tiempo presente**, sin mayúscula inicial ni punto final.

---

#### 🧾 2. **Descripción del PR**

Debes incluir secciones claras y completas como:

##### **## Description**

Breve explicación de lo que hace la PR.

##### **## Changes**

Lista detallada de los cambios realizados, idealmente en bullet points:

* Qué archivos fueron creados o modificados
* Qué funcionalidad se agregó o ajustó

##### **## Test**

Pasos para probar el cambio (manual o automático), por ejemplo:

1. Ejecutar el servidor con `npm run dev`
2. Probar endpoint `/api/data`
3. Verificar que la respuesta contenga la información esperada

---

#### 🔖 3. **Etiquetas del PR**

Es **recomendado** usar etiquetas para clarificar la naturaleza del cambio. Algunas comunes:

| Etiqueta                        | Uso                              |
| ------------------------------- | -------------------------------- |
| `feat`                          | Nueva funcionalidad              |
| `fix`                           | Corrección de error              |
| `build`, `ci`, `test`, `style`  | Cambios técnicos                 |
| `do-not-merge/work-in-progress` | Aún en desarrollo                |
| `approved`                      | PR validada por los responsables |
| `security`, `dependencies`      | Cambios críticos o externos      |
| `hotfix`                        | Corrección urgente en producción |

Más etiquetas están documentadas y pueden combinarse según sea necesario.

---

#### 🛑 4. **Restricciones Importantes**

* ❌ **NO se permite hacer squash** de commits en PRs internos.
* ❌ **NO hacer amend y push -f** una vez abierta la PR.
* ✔️ El historial de commits debe mantenerse limpio y detallado.

---
```
- **Uso**: Definición completa de requerimientos funcionales y no funcionales que guiaron el diseño de la solución.

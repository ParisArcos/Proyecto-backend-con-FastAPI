# Task Management API

API REST para la gestión de tareas desarrollada con FastAPI.

## Instalación

### 1. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias para desarrollo local

```bash
pip install -r requirements.txt
```

### 3. Levantar la API y PostgreSQL con Docker

```bash
docker compose up -d
```

### 4. Ejecutar la aplicación fuera de Docker

```bash
# Opción 1: Comando moderno de FastAPI (recomendado)
fastapi dev main.py --port 8080

# Opción 2: Uvicorn tradicional
uvicorn main:app --reload --port 8080

# Opción 3: Python directo
python3 main.py
```

## Endpoints

### TODO: Documentar todos los endpoints

- `GET /` - Información de la API
- `POST /tasks/` - Crear una nueva tarea
- `GET /tasks/{task_id}` - Obtener una tarea por ID
- `PUT /tasks/{task_id}/completar` - Marcar una tarea como completada
- `GET /tasks/caducadas` - Obtener lista de tareas caducadas

## Ejecutar tests

```bash
python3 test_api.py
```

## Documentación interactiva

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

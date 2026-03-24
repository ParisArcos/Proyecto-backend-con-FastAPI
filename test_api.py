from datetime import date, timedelta

import requests

BASE_URL = "http://localhost:8000"


def create_task(payload):
    response = requests.post(f"{BASE_URL}/tasks/", json=payload)
    return response


def test_crear_tarea():
    payload = {
        "titulo": "Estudiar FastAPI",
        "contenido": "Repasar rutas y modelos",
        "deadline": (date.today() + timedelta(days=2)).isoformat(),
    }

    response = create_task(payload)
    assert response.status_code == 201

    data = response.json()
    assert data["titulo"] == payload["titulo"]
    assert data["contenido"] == payload["contenido"]
    assert data["deadline"] == payload["deadline"]
    assert data["completada"] is False

    return data["id"]


def test_obtener_tarea():
    payload = {
        "titulo": "Leer documentacion",
        "contenido": "Leer la documentacion oficial",
        "deadline": (date.today() + timedelta(days=3)).isoformat(),
    }

    created_response = create_task(payload)
    task_id = created_response.json()["id"]

    response = requests.get(f"{BASE_URL}/tasks/{task_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task_id
    assert data["titulo"] == payload["titulo"]


def test_marcar_completada():
    payload = {
        "titulo": "Hacer ejercicios",
        "contenido": "Practicar Python",
        "deadline": (date.today() + timedelta(days=1)).isoformat(),
    }

    created_response = create_task(payload)
    task_id = created_response.json()["id"]

    response = requests.put(f"{BASE_URL}/tasks/{task_id}/completar")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task_id
    assert data["completada"] is True


def test_obtener_tareas_caducadas():
    payload = {
        "titulo": "Tarea vencida",
        "contenido": "Esta tarea ya deberia estar caducada",
        "deadline": (date.today() - timedelta(days=1)).isoformat(),
    }

    created_response = create_task(payload)
    task_id = created_response.json()["id"]

    response = requests.get(f"{BASE_URL}/tasks/caducadas")
    assert response.status_code == 200

    data = response.json()
    expired_ids = [task["id"] for task in data]
    assert task_id in expired_ids


def test_datos_incorrectos():
    payload = {
        "titulo": "",
        "contenido": "Datos no validos",
        "deadline": "fecha-incorrecta",
    }

    response = requests.post(f"{BASE_URL}/tasks/", json=payload)
    assert response.status_code in [400, 422]


if __name__ == "__main__":
    print("Ejecutando tests...")
    test_crear_tarea()
    print("test_crear_tarea OK")
    test_obtener_tarea()
    print("test_obtener_tarea OK")
    test_marcar_completada()
    print("test_marcar_completada OK")
    test_obtener_tareas_caducadas()
    print("test_obtener_tareas_caducadas OK")
    test_datos_incorrectos()
    print("test_datos_incorrectos OK")
    print("Tests completados")

import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

# Helpers para construir URLs
def tasks_list_url():
    return "/api/tasks/"

def task_detail_url(task_id: int):
    return f"/api/tasks/{task_id}/"

def task_complete_url(task_id: int):
    return f"/api/tasks/{task_id}/complete/"

@pytest.mark.django_db
def test_auth_required(api_client):
    resp = api_client.get(tasks_list_url())
    assert resp.status_code == 401

@pytest.mark.django_db
def test_list_own_tasks_only(auth_client, user, task_factory, other_user):
    # Tareas de otro usuario
    task_factory(owner=other_user, title="Otro 1")
    task_factory(owner=other_user, title="Otro 2")
    # Tareas del autenticado
    task_factory(owner=user, title="Mia 1")
    task_factory(owner=user, title="Mia 2")

    resp = auth_client.get(tasks_list_url())
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.data["results"]] if "results" in resp.data else [t["title"] for t in resp.data]
    assert "Mia 1" in titles and "Mia 2" in titles
    assert "Otro 1" not in titles and "Otro 2" not in titles

@pytest.mark.django_db
def test_create_task(auth_client):
    payload = {"title": "Estudiar DRF", "description": "tutorial oficial"}
    resp = auth_client.post(tasks_list_url(), payload, format="json")
    assert resp.status_code == 201
    assert resp.data["title"] == payload["title"]
    assert resp.data["description"] == payload["description"]
    assert resp.data["is_completed"] is False

@pytest.mark.django_db
def test_retrieve_update_delete_task(auth_client, user, task_factory):
    task = task_factory(owner=user, title="Original")

    # retrieve
    r = auth_client.get(task_detail_url(task.id))
    assert r.status_code == 200
    assert r.data["title"] == "Original"

    # patch
    r = auth_client.patch(task_detail_url(task.id), {"title": "Edited"}, format="json")
    assert r.status_code == 200 and r.data["title"] == "Edited"

    # delete
    r = auth_client.delete(task_detail_url(task.id))
    assert r.status_code == 204

@pytest.mark.django_db
def test_cannot_access_others_task(auth_client, task_factory, other_user):
    other_task = task_factory(owner=other_user, title="Ajena")
    # detalle
    r = auth_client.get(task_detail_url(other_task.id))
    assert r.status_code in (403, 404)  # según tu permiso IsOwner puedes devolver 404
    # delete
    r = auth_client.delete(task_detail_url(other_task.id))
    assert r.status_code in (403, 404)

@pytest.mark.django_db
def test_complete_action(auth_client, user, task_factory):
    task = task_factory(owner=user, is_completed=False)
    r = auth_client.post(task_complete_url(task.id))
    assert r.status_code == 200
    assert r.data['status'] == 'task marked as completed'

@pytest.mark.django_db
def test_search_and_filters(auth_client, user, task_factory):
    u = user
    old = task_factory(owner=u, title="Vieja tarea", description="aprender cosas", is_completed=False)
    from todo.models import Task
    Task.objects.filter(pk=old.pk).update(creation_date=timezone.now() - timedelta(days=3))

    task_factory(owner=u, title="Nueva", description="tutorial", is_completed=False)
    task_factory(owner=u, title="Otra", description="sin texto", is_completed=True)

    # search por contenido
    r = auth_client.get(tasks_list_url() + "?search=Nueva")
    assert r.status_code == 200
    titles = [t["title"] for t in (r.data["results"] if "results" in r.data else r.data)]
    assert "Nueva" in titles
    assert "Otra" not in titles

    # filtro por estado
    r = auth_client.get(tasks_list_url() + "?is_completed=true")
    titles = [t["title"] for t in (r.data["results"] if "results" in r.data else r.data)]
    assert "Otra" in titles and "Nueva" not in titles

    # filtro por fecha (solo recientes)
    iso_from = (timezone.now() - timedelta(days=1)).replace(microsecond=0).isoformat() + "Z"
    r = auth_client.get(tasks_list_url() + f"?created_from={iso_from}")
    titles = [t["title"] for t in (r.data["results"] if "results" in r.data else r.data)]
    assert "Nueva" in titles and "Vieja tarea" not in titles

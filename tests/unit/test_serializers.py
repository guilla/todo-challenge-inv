import pytest
from rest_framework.test import APIRequestFactory
from todo.serializers import TodoSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_task_serializer_create_sets_owner():
    user = User.objects.create_user("u1", password="x")
    factory = APIRequestFactory()
    request = factory.post("/api/tasks/", {"title": "Aprender DRF", "description": ""}, format="json")
    request.user = user

    serializer = TodoSerializer(data={"title": "Aprender DRF", "description": ""}, context={"request": request})
    assert serializer.is_valid(), serializer.errors
    task = serializer.save()

    assert task.owner == user
    assert task.title == "Aprender DRF"

@pytest.mark.django_db
def test_task_serializer_read_only_fields():
    user = User.objects.create_user("u1", password="x")
    factory = APIRequestFactory()
    request = factory.post("/api/tasks/", {"title": "X"}, format="json")
    request.user = user
    s = TodoSerializer(data={"title": "X", "created_at": "2030-01-01T00:00:00Z"}, context={"request": request})
    assert s.is_valid(), s.errors
    task = s.save()
    # created_at lo setea el modelo, no el input
    assert task.creation_date is not None

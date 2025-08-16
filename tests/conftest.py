import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from model_bakery import baker
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(username="gonzalo", email="g@example.com", password="superseguro123")

@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="otro", email="o@example.com", password="pass123456")

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client(user):
    """
    APIClient with Authorization: Bearer <access> (SimpleJWT)
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    client = APIClient()
    access = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return client

@pytest.fixture
def task_factory(db):
    """
    Task factory.
    """
    from todo.models import Task
    def _make(**kwargs):
        return baker.make(Task, **kwargs)
    return _make

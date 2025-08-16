import pytest
from todo.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_task_str():
    user = User.objects.create_user("u1", password="x")
    t = Task.objects.create(owner=user, title="T1")
    assert "T1" in str(t)

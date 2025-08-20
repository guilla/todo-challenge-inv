from rest_framework import viewsets, permissions, status, generics, decorators
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Task
from .serializers import TodoSerializer, UserSerializer
from .filters import TaskFilter
from .permissions import IsOwner
import logging
from logging_utils import log_event, TASK_ACTIONS

User = get_user_model()
logger = logging.getLogger(__name__)
class UserRegistrationView(generics.CreateAPIView):
    """New user registration.

        POST /api/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to register

class TaskViewSet(viewsets.ModelViewSet):
    """CRUD operations for tasks.

        GET /api/tasks/
        POST /api/tasks/
        GET /api/tasks/{id}/
        PUT /api/tasks/{id}/
        DELETE /api/tasks/{id}/
    """
    serializer_class = TodoSerializer
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['creation_date', 'title']

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user).order_by('-creation_date')

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'complete']:
            permission_classes.append(IsOwner)
        return [permission() for permission in permission_classes]

    # ----- CREATE -----
    def perform_create(self, serializer):
        instance = serializer.save(owner=self.request.user)
        # log después de guardar
        log_event(self.request, "task_created",
                  task_id=instance.id, title=instance.title, status=status.HTTP_201_CREATED)

    # ----- UPDATE (PUT/PATCH) -----
    def perform_update(self, serializer):
        instance = serializer.save()
        log_event(self.request, "task_updated",
                  task_id=instance.id, title=instance.title, status=status.HTTP_200_OK)

    # ----- DELETE -----
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        task_id, title = instance.id, instance.title
        resp = super().destroy(request, *args, **kwargs)
        log_event(request, "task_deleted",
                  task_id=task_id, title=title, status=resp.status_code)
        return resp

    # ----- RETRIEVE (GET /{id}/) -----
    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        obj = self.get_object()
        log_event(request, "task_retrieved",
                  task_id=obj.id, title=obj.title, status=resp.status_code)
        return resp

    # ----- LIST (GET /) -----
    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        count = len(resp.data["results"]) if isinstance(resp.data, dict) and "results" in resp.data else len(resp.data)
        log_event(request, "task_listed",
                  result_count=count, status=resp.status_code)
        return resp

    @decorators.action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a task as completed.

            POST /api/tasks/{id}/complete/
        """

        task = self.get_object()
        if task.is_completed:
            logger.info("task_already_completed", extra={"request_id": getattr(self.request, "request_id", "-"), "task_id": task.id})
            return Response({'status': 'task already completed'}, status=status.HTTP_200_OK)
        task.is_completed = True
        task.save()
        logger.info("task_created", extra={"request_id": getattr(self.request, "request_id", "-"), "task_id": task.id})
        return Response({'status': 'task marked as completed'}, status=status.HTTP_200_OK)

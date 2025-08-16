from rest_framework import viewsets, permissions, status, generics, decorators
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Task
from .serializers import TodoSerializer, UserSerializer
from .filters import TaskFilter
from .permissions import IsOwner

User = get_user_model()

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

    @decorators.action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a task as completed.

            POST /api/tasks/{id}/complete/
        """
        task = self.get_object()
        if task.is_completed:
            return Response({'status': 'task already completed'}, status=status.HTTP_200_OK)
        task.is_completed = True
        task.save()
        return Response({'status': 'task marked as completed'}, status=status.HTTP_200_OK)

import django_filters
from .models import Task

class TaskFilter(django_filters.FilterSet):
    
    class Meta:
        model = Task
        fields = {
            'is_completed': ['exact'],
            'creation_date': ['gte', 'lte'],
            'title': ['icontains'],
        }
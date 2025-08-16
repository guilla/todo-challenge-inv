import django_filters
from .models import Task

class TaskFilter(django_filters.FilterSet):
    created_from = django_filters.IsoDateTimeFilter(field_name="creation_date", lookup_expr="gte")
    created_to   = django_filters.IsoDateTimeFilter(field_name="creation_date", lookup_expr="lte")
    is_completed = django_filters.BooleanFilter(field_name="is_completed")

    class Meta:
        model = Task
        fields = ["is_completed", "created_from", "created_to"]

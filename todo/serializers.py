from rest_framework import serializers
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'owner', 'title', 'description', 'creation_date', 'is_completed']
        read_only_fields = ['id', 'creation_date', 'owner']

    def create(self, validated_data):
        user = self.context["request"].user
        return Task.objects.create(owner=user, **validated_data)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

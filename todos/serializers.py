from rest_framework import serializers
from .models import Todo
class TodoSerializer(serializers.ModelSerializer):
  id = serializers.ReadOnlyField()
  class Meta:
    model = Todo
    fields = '__all__'
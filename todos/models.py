from django.db import models

# Create your models here.
class Todo(models.Model):
  isCompleted = models.BooleanField(default=False)
  content = models.CharField(max_length=200)
  created_at = models.DateTimeField(auto_now_add=True)
  order = models.FloatField(null=True)
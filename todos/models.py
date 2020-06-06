from django.db import models


class Todo(models.Model):
    isCompleted = models.BooleanField(default=False)
    content = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.FloatField(null=True)

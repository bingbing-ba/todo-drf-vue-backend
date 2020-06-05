from django.urls import path
from . import views
urlpatterns = [
  path('todo/', views.cr_todo),
  path('todo/<int:id>', views.ud_todo),
]
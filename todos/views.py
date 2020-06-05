from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Todo
from .serializers import TodoSerializer
# Create your views here.

@api_view(['GET','POST'])
def cr_todo(request):
  if request.method == 'GET':
    todos = Todo.objects.all().order_by('order')
    serializer = TodoSerializer(todos, many=True)
    result = serializer.data
  else:
    serializer = TodoSerializer(data=request.data)
    if serializer.is_valid():
      tmp = serializer.save()
      serializer.save(order=tmp.id)
      result = {
        'status': 'success',
        **serializer.data,
      }
    else:
      result = {
        'status':'failure',
        'error':'invalid request'
      }
  return Response(data=result)

  
@api_view(['PATCH','DELETE'])
def ud_todo(request,id):
  todo = get_object_or_404(Todo,id=id)
  if request.method == 'PATCH':
    serializer = TodoSerializer(instance=todo,data=request.data)
    if serializer.is_valid():
      serializer.save()
      result = {
        'status': 'success',
        **serializer.data
      }
    else:
      result = {
        'status': 'failure',
        'error': 'invalid request',
      }
  else:
    todo.delete()
    result = {
      'status':'success'
    }
  return Response(data=result)
    
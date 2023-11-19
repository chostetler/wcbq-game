from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse("Hello world, you are at the quizgame index")

def room(request, room_name):
    return render(request, 'quizgame/room.html', {'room_name': room_name})

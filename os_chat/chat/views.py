from django.shortcuts import render ,redirect
from django.http import HttpResponse


def index(request):
    if request.method == 'POST':
        user_input = request.POST.get('message-input', '') 
        print(user_input)
    return render(request , template_name = "chat/main.html")

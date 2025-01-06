from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, 'login.html')

@login_required
def home_view(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def supplies_view(request):
    return render(request, 'supplies.html')


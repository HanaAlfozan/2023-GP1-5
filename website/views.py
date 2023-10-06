from django.shortcuts import render
from django.http import HttpResponse

def Game(request):
    return render(request,"Games.html" )

def Fav(request):
    return render(request,"Fav.html" )

def index(request):
    return render(request,"index.html" )

def edit(request):
    return render(request,"editprofile.html" )

def login(request):
    return render(request,"login.html" )

def profile(request):
    return render(request,"profile.html" )

def History(request):
    return render(request,"History.html" )

def signup(request):
    return render(request,"signup.html" )

def estimate(request):
    return render(request,"AgeEstimation.html" )

def game_info_page(request):
    img = request.GET.get('img')
    context = {
        'img': img,
    }
    return render(request, 'GameInfoPage.html', context)
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

def log_in(request):
    return render(request,"log-in.html" )

def profile(request):
    return render(request,"profile.html" )

def History(request):
    return render(request,"History.html" )

def signup(request):
    return render(request,"signup.html" )

def contact(request):
    return render(request,"contact.html" )

def about(request):
    return render(request,"about.html" )

def estimate(request):
    return render(request,"AgeEstimation.html" )



def custom_password_reset_form(request):
    return render(request,"custom_password_reset_form.html" )

def game_info_page(request, game_id):
    return render(request, 'GameInfoPage.html', {'game_id': game_id})
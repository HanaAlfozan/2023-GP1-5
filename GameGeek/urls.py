"""
URL configuration for GameGeek project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from AgeEstimationModel import views as AgeEstimationModel_views
from FrontEnd import views
from BackEnd import views as BackEnd_views
from FrontEnd import views as Frontend_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('Games/',views.Game,name='Games'),
    path('Fav/',views.Fav,name='Fav'),
    path('History/',views.History,name='History'),
    path('login/',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('profile/',views.profile,name='profile'),
    path('AgeEstimation/',views.estimate,name='estimate'),
    path('GameInfoPage/', views.game_info_page, name='game_info_page'),
    path('contact/',views.contact,name='contact'),
    path('about/',views.about,name='about'),
    path('AgeEstimation/Games.html', views.Game,name='Games'),
    path('AgeEstimationModel/process_image/', AgeEstimationModel_views.process_image, name='process_image'),
    path('BackEnd/SignupUser/', BackEnd_views.SignupUser, name='SignupUser'),
    path('AgeEstimation/',Frontend_views.estimate, name='estimat'),
    path('signup/',Frontend_views.signup,name='signup'),
    path('login/',Frontend_views.login,name='login'),
    path('BackEnd/LoginUser/', BackEnd_views.LoginUser, name='LoginUser'),
    path('BackEnd/AssignAgeGroup/', BackEnd_views.AssignAgeGroup, name='AssignAgeGroup'),
    path('Games/',Frontend_views.Game,name='Games'),
    path('BackEnd/Hello/', BackEnd_views.Hello, name='Hello'),
    path('BackEnd/GetProfileData/', BackEnd_views.GetProfileData, name='GetProfileData'),
    path('BackEnd/LogoutUser/', BackEnd_views.LogoutUser, name='LogoutUser'),
    path('BackEnd/EditNames/', BackEnd_views.EditNames, name='EditNames'),
    path('BackEnd/custom_password_reset_confirm/', BackEnd_views.custom_password_reset_confirm, name='password_reset'),
    path('reset/<str:uidb64>/<str:token>/', BackEnd_views.custom_password_reset_confirm, name='password_reset'),
    path('BackEnd/custom_password_reset/', BackEnd_views.custom_password_reset, name='custom_password_reset'),
    path('BackEnd/retrieve_all_games/', BackEnd_views.retrieve_all_games, name='retrieve_all_games'),
    path('game_info_page/<int:game_id>/', views.game_info_page, name='game_info_page'),
    path('BackEnd/retrieve_game_info/', BackEnd_views.retrieve_game_info, name='retrieve_game_info'),
    path('BackEnd/retrieve_random_high_rated_games/', BackEnd_views.retrieve_random_high_rated_games, name='retrieve_random_high_rated_games'),
    path('BackEnd/custom_assigining_ageGroup/', BackEnd_views.custom_assigining_ageGroup, name='custom_assigining_ageGroup'),
    path('assign-age-group/<str:uidb64>/<str:token>/', BackEnd_views.custom_assigining_ageGroup_confirm, name='custom_assigining_ageGroup_confirm'),
    path('BackEnd/custom_assigining_ageGroup_confirm/', BackEnd_views.custom_assigining_ageGroup_confirm, name='custom_assigining_ageGroup_confirm'),
    path('BackEnd/send_email/', BackEnd_views.send_email, name='send_email'),

    
]

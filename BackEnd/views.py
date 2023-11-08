from .models import GGUser
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import json
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User


def SignupUser(request):
    if request.method == 'POST':
        username = request.POST['Username']
        email = request.POST['Email']
        password = request.POST['Password']
        confirm_password = request.POST['confirm_password']
        Accept_conditions = request.POST.get('Accept_conditions') == 'on'

        if password == confirm_password:
            if GGUser.objects.filter(Email=email).exists():
                messages.error(request, "Email Already Exists!")
            elif GGUser.objects.filter(Username=username).exists():
                messages.error(request, "Username Already Exists!")
            else:
                user = GGUser.objects.create_user(
                    Username=username,
                    Email=email,
                    Password=password,
                    Accept_conditions=Accept_conditions
                )
                user_id = user.User_ID
                request.session['user_id'] = user_id
                return redirect('estimate')

        else:
            messages.error(request, "Password Mismatch!")

    return redirect('signup')



def LoginUser(request):
    if request.method == 'POST':
        username = request.POST['Username']
        password = request.POST['Password']
        try:
            user = GGUser.objects.get(Username=username)
        except GGUser.DoesNotExist:
            user = None

        if user and user.check_password(password):
            login(request, user)
            user_id = user.User_ID
            request.session['user_id'] = user_id
            return redirect('estimate')
        else:
            messages.error(request, 'Invalid username or password')
    return redirect('login')


   

def AssignAgeGroup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            estimated_age_group = data.get('estimatedAgeGroup')
            prevPage =  data.get('previousPage')
            user_id = request.session.get('user_id')
            user = GGUser.objects.get(User_ID=user_id)
            CameFromSignUp = 'signup'
            CameFromLogIn = 'login'
            if CameFromSignUp in prevPage:
                try:
                   user.Age_group = estimated_age_group
                   user.save()
                   return JsonResponse({'message': 'Age Group updated successfully'})
                except GGUser.DoesNotExist:
                   return JsonResponse({'error': 'User not found'}, status=404)

            elif  CameFromLogIn in prevPage:
                try:
                    if(user.Age_group == estimated_age_group):
                       return JsonResponse({'message': 'Age group checked successfully'})
                    else:
                       messages.error(request, "Age group Missmatch, try again!")
                       return redirect('estimate')
                except GGUser.DoesNotExist:
                       return JsonResponse({'error': 'User not found'}, status=404)       


        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)



def Hello(request):
    user_id = request.session.get('user_id')
    if user_id is not None:
        try:
            user = GGUser.objects.get(User_ID=user_id)
            user_info = {
                'Username': user.Username,
                'Age_group': user.Age_group,
            }
            return JsonResponse(user_info)
        except GGUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=400)
    else:
        return JsonResponse({'error': 'User ID not found in session'}, status=400)




def GetProfileData(request):
    user_id = request.session.get('user_id')
    if user_id is not None:
        try:
            user = GGUser.objects.get(User_ID=user_id)
            profile_data = {
                'Username': user.Username,
                'Age_group': user.Age_group,
                'First_name': user.First_name,
                'Last_name': user.Last_name,
                'Email': user.Email,
                'Date_joined': user.Date_joined.strftime('%m/%d/%Y'),
        }
            return JsonResponse(profile_data)
        except GGUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=400)
    else:
        return JsonResponse({'error': 'User not authenticated'})


def LogoutUser(request):  
    logout(request)
    return redirect('index')     

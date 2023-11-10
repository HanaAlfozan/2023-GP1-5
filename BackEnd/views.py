from .models import GGUser
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import json
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetView
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import HttpResponseNotFound

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


def custom_password_reset(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = GGUser.objects.get(Email=email)
        except GGUser.DoesNotExist:
            return HttpResponseNotFound('Email not found')

        # Generate a token and uid for the user
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Create the reset link
        reset_link = f"{request.scheme}://{request.get_host()}/reset/{uid}/{token}/"

        # Send the email with the reset link
        send_mail(
            'Password Reset',
            f'Dear Gamer, use the following link to reset your password: {reset_link}',
            'gamegeekwebsite@gmail.com',
            [email],
            fail_silently=False,
        )
        if 'error_message' in request.POST:
            return HttpResponse(status=400)

        return HttpResponse(status=200) 

    return render(request, 'login.html')


def custom_password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = GGUser.objects.get(User_ID=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Valid token, allow the user to set a new password
        if request.method == 'POST':
            # Process the form to set a new password
            password = request.POST['password']
            confirm_password = request.POST['password2']
            if password == confirm_password:
              user.set_password(password)
              user.save()
              return render(request, 'login.html', {'status': 'reset', 'message': 'Password reset'})
            else:
              messages.error(request, "Password Mismatch!")  
        return render(request, 'login.html', {'status': 'confirm', 'message': 'Password confirm'})
    else:
        error_message = 'Unexpected error occured, please try again'
        return render(request, 'login.html', {'status': 'error', 'message': 'Password reset ' + error_message})



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

def EditNames(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if user_id is not None:
            try:
                user = GGUser.objects.get(User_ID=user_id)

                # Update the user's profile based on the POST data
                user.First_name = request.POST.get('First_name', user.First_name)
                user.Last_name = request.POST.get('Last_name', user.Last_name)
                user.save()

                profile_data = {
                    'First_name': user.First_name,
                    'Last_name': user.Last_name,
                }
                return JsonResponse(profile_data)
            except GGUser.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=400)
        else:
            return JsonResponse({'error': 'User not authenticated'})
    else:
        return JsonResponse({'error': 'Invalid request method. POST expected'}, status=400)

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
from .models import GamesList
import re
from django.core.paginator import Paginator, EmptyPage
import random
import math
from django.db.models import Case, When, Value, IntegerField


def SignupUser(request):
    if request.method == 'POST':
        username = request.POST['Username']
        email = request.POST['Email']
        password = request.POST['Password']
        confirm_password = request.POST['confirm_password']
        Accept_conditions = request.POST.get('Accept_conditions') == 'on'

        if password == confirm_password:
            if GGUser.objects.filter(Username=username).exists():
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
        username = request.POST['username']
        try:
            user = GGUser.objects.get(Username=username)
        except GGUser.DoesNotExist:
            return HttpResponseNotFound('Username not found')

        # Generate a token and uid for the user
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        email = user.Email

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

def custom_assigining_ageGroup(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = GGUser.objects.get(User_ID=user_id)
                email = user.Email
                # Continue with your logic using the email
            except GGUser.DoesNotExist:
                return HttpResponseNotFound('User not found')

        # Generate a token and uid for the user
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        email = user.Email

        # Create the reset link for age group assignment
        reset_link = f"{request.scheme}://{request.get_host()}/assign-age-group/{uid}/{token}/"

        # Send the email with the reset link
        send_mail(
            'Assigning Age Group',
            f'Dear Gamer, we apologize for the issue you encountered. Please click this link to assign your age group: {reset_link}',
            'gamegeekwebsite@gmail.com',
            [email],
            fail_silently=False,
        )
        if 'error_message' in request.POST:
            return HttpResponse(status=400)
        return HttpResponse(status=200)

    return render(request, 'AgeEstimation.html')

def custom_assigining_ageGroup_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = GGUser.objects.get(User_ID=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
            if request.method == 'POST':
        # Valid token, allow the user to set a new password
              ageGroup = request.POST.get('ageGroup')
              user.Approved_age_group = ageGroup
              user.save()
              return render(request, 'AgeEstimation.html', {'status': 'done', 'message': 'Done'})
            return render(request, 'AgeEstimation.html', {'status': 'confirm', 'message': 'Assign confirm'})
    else:
        error_message = 'Unexpected error occured, please try again'
        return render(request, 'AgeEstimation.html', {'status': 'error', 'message': error_message})



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
            return redirect('Games')
        else:
            messages.error(request, 'Invalid username or password')
    return redirect('login')
 

def AssignAgeGroup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            estimated_age_group = data.get('estimatedAgeGroup')
            user_id = request.session.get('user_id')
            user = GGUser.objects.get(User_ID=user_id)
            try:
                user.Approved_age_group = estimated_age_group
                user.save()
                return JsonResponse({'message': 'Age Group updated successfully'})
            except GGUser.DoesNotExist:
                   return JsonResponse({'error': 'User not found'}, status=404)

        except GGUser.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)       

def Hello(request):
    user_id = request.session.get('user_id')
    if user_id is not None:
        try:
            user = GGUser.objects.get(User_ID=user_id)

            user_info = {
                'Username': user.Username,
                'Age_group': user.Approved_age_group,
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
                'Age_group': user.Approved_age_group,
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




def retrieve_all_games(request):


    user_id = request.session.get('user_id')

    if user_id is not None:
        try:
            user = GGUser.objects.get(User_ID=user_id)
            user_age_group_str = user.Approved_age_group

            # Function to extract the numeric part from age group strings
            def extract_numeric_part(age_group):
                return int(age_group[:-1])

            # Convert user age group string to numerical value
            user_age_group = extract_numeric_part(
                user_age_group_str) if user_age_group_str and user_age_group_str != 'fals' else 12
        except GGUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'})
    else:
        return JsonResponse({'error': 'User not authenticated'})

    # Retrieve objects from the GamesList model suitable for the user's approved age group
    if user_age_group == 17:
        # If the user has the highest age group, retrieve all games
        all_games_data = GamesList.objects.all()
    else:
        # Use Case and When to handle age group comparison
        all_games_data = GamesList.objects.annotate(
            numeric_age_rating=Case(
                When(Age_Rating='4+', then=Value(4)),
                When(Age_Rating='9+', then=Value(9)),
                When(Age_Rating='12+', then=Value(12)),
                When(Age_Rating='17+', then=Value(17)),
                default=Value(0),  # Default case, adjust as needed
                output_field=IntegerField(),
            )
        ).filter(numeric_age_rating__lte=user_age_group)








    slice_number = int(request.GET.get('slice', 0))  # Default to slice 0 if not provided
    items_per_page = 18

    # Use Django Paginator to paginate the data
    paginator = Paginator(all_games_data, items_per_page)
    page_number = int(request.GET.get('page', 1))  # Default to page 1 if not provided

    try:
        current_page_data = paginator.page(page_number)
    except EmptyPage:
        # If the requested page is out of range, return an empty list
        current_page_data = []


    # Convert the current page data to a list of dictionaries with cleaned names
    games_list = [
        {
            'Name': clean_name(game.Name),
            'Icon_URL': game.Icon_URL,
            'Genres': game.Genres,
            'URL': game.URL,
            'Average_User_Rating': game.Average_User_Rating,
            'User_Rating_Count': game.User_Rating_Count,
            'Price': game.Price,
            'In_app_Purchases': game.In_app_Purchases,
            'Developer': game.Developer,
            'Age_Rating': game.Age_Rating,
            'Languages': game.Languages,
            'Size': str(game.Size),  # Convert DecimalField to string
            'Original_Release_Date': game.Original_Release_Date,
            'ID': game.ID,
        }
        for game in current_page_data
    ]

    # Include information about the current page and total pages in the JSON response
    response_data = {
        'games_data': games_list,
        'current_page': current_page_data.number,
        'total_pages': paginator.num_pages,
        'Age':user_age_group,
    }

    # Return a JSON response
    return JsonResponse(response_data)
def clean_name(name):
    # Decode Unicode escape sequences
    name = name.encode().decode('unicode_escape')

    # Check if the name contains a hyphen (-) and if it's not at the beginning
    if '-' in name and not name.startswith('-'):
        # Use a regular expression to remove everything after the first hyphen
        cleaned_name = re.sub(r' - .*', '', name)
    else:
        cleaned_name = name

    # Check if the name contains a backslash (\) and if it's not at the beginning
    if '\\' in cleaned_name:
        # If the backslash is at the beginning, remove it and all values after it until a capital letter
        if cleaned_name.startswith('\\'):
            cleaned_name = re.sub(r'\\([^A-Z]*)', r'\1', cleaned_name)
        else:
            # If the backslash is not at the beginning, remove everything after the first backslash, excluding capital letters
            cleaned_name = re.sub(r'\\([^A-Z]*[A-Z].*)', r'\1', cleaned_name)

    return cleaned_name


def clean_description(description):
    # Remove URLs
    description=description.encode().decode('unicode_escape')
    description_without_urls = re.sub(r'http\S+|www\S+|https\S+', '', description, flags=re.MULTILINE)
    # Remove emails
    description_without_emails = re.sub(r'\S+@\S+', '', description_without_urls, flags=re.MULTILINE)



    # Ensure the description ends with a period
    if not description_without_emails.endswith('.'):
        description_without_emails += '.'

    return description_without_emails







def retrieve_game_info(request):
    # Retrieve the game ID from the request parameters
    game_id = request.GET.get('ID')

    print('Received game ID:', game_id)  # Check if the ID is received in the server console

    # Retrieve the game object based on the game ID
    try:
        game = GamesList.objects.get(ID=game_id)

        # Clean the game description
        cleaned_description = clean_description(game.Description)
        dev = clean_dev(game.Developer)

        cleaned_name = clean_name(game.Name)
        # Convert the game object to a dictionary with the cleaned description
        game_info = {
            'Name': cleaned_name,
            'Icon_URL': game.Icon_URL,
            'Description': cleaned_description,
            'Genres': game.Genres + '.',
            'URL': game.URL,
            'Average_User_Rating': game.Average_User_Rating + '.',
            'User_Rating_Count': game.User_Rating_Count + '.',
            'Price': game.Price,
            'In_app_Purchases': game.In_app_Purchases,
            'Developer': dev,
            'Age_Rating': game.Age_Rating,
            'Languages': game.Languages + '.',
            'Size': str(game.Size),  # Convert DecimalField to string
            'Original_Release_Date': game.Original_Release_Date + '.',
        }
        return JsonResponse({'games_data': game_info})
    except GamesList.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)

def retrieve_random_high_rated_games(request):
    # Retrieve all objects from the GamesList model
    all_games_data = list(GamesList.objects.all())

    # Ensure that the total number of games is at least 12
    if len(all_games_data) < 12:
        return JsonResponse({'error': 'Not enough games available'}, status=400)


    first_12_high_rated_games = all_games_data[12:24]

    # Convert the first 12 high-rated games to a list of dictionaries with cleaned names
    games_list = [
        {
            'Name': clean_name(game.Name),
            'Icon_URL': game.Icon_URL,
            'Genres': game.Genres,
            'URL': game.URL,
            'Average_User_Rating': game.Average_User_Rating,
            'User_Rating_Count': game.User_Rating_Count,
            'Price': game.Price,
            'In_app_Purchases': game.In_app_Purchases,
            'Developer': game.Developer,
            'Age_Rating': game.Age_Rating,
            'Languages': game.Languages,
            'Size': str(game.Size),  # Convert DecimalField to string
            'Original_Release_Date': game.Original_Release_Date,
            'ID': game.ID,
        }
        for game in first_12_high_rated_games
    ]

    # Return a JSON response
    return JsonResponse({'random_high_rated_games_data': games_list})



def clean_dev(dev):
    # Remove URLs
    dev=dev.encode().decode('unicode_escape')

    # Ensure the description ends with a period
    if not dev.endswith('.'):
        dev += '.'

    return dev
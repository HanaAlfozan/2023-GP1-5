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
from .models import GamesList, Favorite, GGUser, Visited
import re
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Case, When, Value, IntegerField, CharField, FloatField, F
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Value, IntegerField, Case, When
from django.db.models.functions import Cast
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib import messages


@csrf_protect
def SignupUser(request):
    print('in SignupUser')
    if request.method == 'POST':
        username = request.POST['Username']
        email = request.POST['Email']
        password = request.POST['Password']
        confirm_password = request.POST['confirm_password']
        Accept_conditions = request.POST.get('Accept_conditions') == 'on'
        SecurityAnswer = request.POST['answer']
        SecurityQuestion = request.POST['securityQuestion']

        if password == confirm_password:
            print('if password == confirm_password')
            if GGUser.objects.filter(Username=username).exists():
                print('Username Already Exists!')
                messages.error(request, "Username Already Exists!")
            else:
                user = GGUser.objects.create_user(
                    Username=username,
                    Email=email,
                    Password=password,
                    Accept_conditions=Accept_conditions,
                    Security_answer=SecurityAnswer,
                    Security_question=SecurityQuestion,
                    )
                user_id = user.User_ID
                request.session['user_id'] = user_id
                return redirect('estimate')
            
            messages.error(request, "Password Mismatch!")
            return redirect('signup')


def AssignAgeGroup(request):
    print('in AssignAgeGroup')
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        try:
            data = json.loads(request.body.decode('utf-8'))
            estimated_age_group = data.get('estimatedAgeGroup')
            print('AssignAgeGroup', estimated_age_group)
            user = GGUser.objects.get(User_ID=user_id)

            if user:
                user.Approved_age_group = estimated_age_group
                user.save()
                return JsonResponse({'message': 'User is active and age group assigned successfully'})


            else:
                return JsonResponse({'error': 'User data not found'}, status=404)

        except GGUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

    return HttpResponse()


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

from django.utils.text import slugify

def custom_username_reset(request):
    Email = request.POST.get('Email', '')
    securityQuestion = request.POST.get('securityQuestion', '')
    answer = request.POST.get('answer', '')

    try:
        answer = slugify(answer)
        user = GGUser.objects.get(Email=Email, Security_question=securityQuestion, Security_answer__iexact=answer)

        # Generate a token and uid for the user
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        email = user.Email

        # Create the reset link
        reset_link = f"{request.scheme}://{request.get_host()}/reset-username/{uid}/{token}/"

        # Send the email with the reset link
        send_mail(
            'Username Reset',
            f'Dear Gamer, use the following link to reset your Username: {reset_link}',
            'gamegeekwebsite@gmail.com',
            [email],
            fail_silently=False,
        )

        if 'error_message' in request.POST:
            return JsonResponse({'error': 'Invalid request'}, status=400)

        return JsonResponse({'success': True})

    except GGUser.DoesNotExist:
        return JsonResponse({'error': 'Username not found'}, status=404)


def custom_assigining_ageGroup(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = GGUser.objects.get(User_ID=user_id)
                email = user.Email
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
            return render(request, 'AgeEstimation.html', {'status': 'verify', 'message': 'verify'})
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


def custom_username_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = GGUser.objects.get(User_ID=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Valid token, allow the user to set a new password
        if request.method == 'POST':
            newusername = request.POST['newusername']
            user.Username = newusername
            user.save()
            return render(request, 'login.html', {'status': 'resetUser', 'message': 'Username reset'})

        return render(request, 'login.html', {'status': 'confirmUser', 'message': 'Username confirm'})
    else:
        error_message = 'Unexpected error occured, please try again'
        return render(request, 'login.html', {'status': 'error', 'message': 'Password reset ' + error_message})


@csrf_protect
def LoginUser(request):
    if request.method == 'POST':
        username = request.POST.get('Username')
        password = request.POST.get('Password')
        try:
            user = GGUser.objects.get(Username=username)
        except GGUser.DoesNotExist:
            user = None

        if user and user.check_password(password):
            if user.email_confirmed:
                login(request, user)
                user_id = user.User_ID
                request.session['user_id'] = user_id
                return redirect('estimate')
            else:
                # Pass a custom message to the template
                print("This message will be printed to the terminal for line 280.")
                # return render(request, 'login.html', {'Emailconfirmation_message': 'account_not_confirmed'})
                messages.error(request,
                               'Your account registration is not confirmed. Please confirm you registration through the link sent to your email.')
                return redirect('login')

        else:
            # Pass a custom message to the template
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    return redirect('login')


def CompareAgeGroups(request):
    print('hi from CompareAgeGroups')
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        try:
            # Parse form-urlencoded data
            estimated_age_group = request.POST.get('estimatedAgeGroup')
            print('here is the received age group:', estimated_age_group)
            user = GGUser.objects.get(User_ID=user_id)
            try:
                if user.Approved_age_group == estimated_age_group:
                    print('Matching')
                    return JsonResponse({'message': 'Matching'})
                else:
                    if (user.Approved_age_group):
                        print('Not Matching - Not null')
                        return JsonResponse({'message': 'Not Matching'})
                    else:
                        print('null')
                        user.delete()
                        return JsonResponse({'message': 'null'})
            except GGUser.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

        except Exception as e:
            print(e)
            return JsonResponse({'error': 'An error occurred'}, status=500)


def SendEmailForWrongEstimation(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = GGUser.objects.get(User_ID=user_id)
                email = user.Email
            except GGUser.DoesNotExist:
                return HttpResponseNotFound('User not found')

        # Generate a token and uid for the user
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        email = user.Email
        agGroup = user.Approved_age_group

        # Create the reset link for age group assignment
        reset_link = f"{request.scheme}://{request.get_host()}/redirect-age-group/{uid}/{token}/"

        # Send the email with the reset link
        send_mail(
            'Redirect Link to Your Assigned Age Group',
            f'Dear Gamer, we noticed that you attempted to log into your account, but it seems there is an issue verifying your assigned age group. Therefore,  you can find the link below to be redirected to your account with your assigned age group: {reset_link}',
            'gamegeekwebsite@gmail.com',
            [email],
            fail_silently=False,
        )
        if 'error_message' in request.POST:
            return HttpResponse(status=400)
        return JsonResponse({'agGroup': agGroup}, status=200)


def RedirectingToGames(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = GGUser.objects.get(User_ID=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            user_id = user.User_ID
            request.session['user_id'] = user_id
        return render(request, 'Games.html')

    else:
        error_message = 'Unexpected error occured, please try again'
        return render(request, 'index.html', {'status': 'error', 'message': error_message})


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
    cache.clear()
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


from django.core.cache import cache
from django.forms.models import model_to_dict
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Case, When, Value, IntegerField


@require_http_methods(["GET"])
def retrieve_all_games(request):
    sorted_games = request.session.get('games_list', [])
    filtered_categories = request.session.get('filtered_games', [])
    user_id = request.session.get('user_id')
    items_per_page = 15
    all_games_data = []
    filter_status = cache.get('filter_status')
    status = filter_status

    if user_id is not None:
        try:
            user = GGUser.objects.get(User_ID=user_id)
            user_age_group_str = user.Approved_age_group

            # Function to extract the numeric part from age group strings
            def extract_numeric_part(age_group):
                match = re.search(r'\d+', age_group)
                if match:
                    return int(match.group())
                return 0

            # Convert user age group string to numerical value
            user_age_group = extract_numeric_part(
                user_age_group_str) if user_age_group_str and user_age_group_str != 'fals' else 12
        except GGUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'})
    else:
        return JsonResponse({'error': 'User not authenticated'})

    if filter_status == 'no games satisfies the filter':
        filter_status = ''
        cache.set('filter_status', filter_status)
        all_games_data = []


    # Retrieve objects from the GamesList model suitable for the user's approved age group
    elif sorted_games and len(filtered_categories) == 0:
        print("here is sorted_games")
        all_games_data = sorted_games

        # Check if there are filtered categories in the cache
    elif filtered_categories:

        print('HERE HERE filtered_categories')

        all_games_data = filtered_categories

        print(f'The length of filtered_categories is: {len(filtered_categories)}')
        print(f'The length of sorted_games is: {len(sorted_games)}')
        print(f'The length of all_games_data (313) is: {len(all_games_data)}')

        if sorted_games:
            all_games_ids = {game['ID'] for game in all_games_data}
            print(f'Before reordering, the ID of the first game is: {all_games_data[0]["ID"]}')
            filtered_sorted_games = [game for game in sorted_games if game['ID'] in all_games_ids]
            print(f'After reordering, the ID of the first game is: {filtered_sorted_games[0]["ID"]}')
            all_games_data = filtered_sorted_games
            print(f'The length of all_games_data (317) is: {len(all_games_data)}')




    else:
        if user_age_group == 17:
            # If the user has the highest age group, retrieve all games
            all_games_data = GamesList.objects.all()
            print('HEREEE EVERTHING')
        else:
            # Use Case and When to handle age group comparison
            print('HERE 123')
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

        ################################AFTER HANDLING ALL CASES NOW DIVIDE THE GAMES########################################

    slice_number = int(request.GET.get('slice', 0))  # Default to slice 0 if not provided

    # Use Django Paginator to paginate the data
    # all_games_data = all_games_data.order_by('Name')
    paginator = Paginator(all_games_data, items_per_page)
    page_number = int(request.GET.get('page', 1))

    try:
        current_page_data = paginator.page(page_number)
    except EmptyPage:
        # If the requested page is out of range, return an empty list
        current_page_data = []

    games_list = []

    if all(isinstance(game, GamesList) for game in current_page_data):
        games_list = [
            {
                'Name': clean_name(game.Name),
                'Icon_URL': game.Icon_URL,
                'URL': game.URL,
                'ID': game.ID,
            }
            for game in current_page_data
        ]
    else:
        # If all_games_data is a list of dictionaries
        games_list = [
            {
                'Name': clean_name(game.get('Name', '')),  # Use get to handle missing keys
                'Icon_URL': game.get('Icon_URL', ''),
                'URL': game.get('URL', ''),
                'ID': game.get('ID', ''),
            }
            for game in current_page_data
        ]
    # Include information about the current page and total pages in the JSON response
    response_data = {
        'games_data': games_list,
        'current_page': current_page_data.number,
        'total_pages': paginator.num_pages,
        'Age': user_age_group,
        'Count': len(games_list),
        'filter_status': status,
        'session': "sission try",
    }

    # Return a JSON response
    # cache.clear()
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
    description = description.encode().decode('unicode_escape')
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
            'Original_Release_Date': game.Original_Release_Date,
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

    first_12_high_rated_games = all_games_data[24:36]

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
    dev = dev.encode().decode('unicode_escape')

    # Ensure the description ends with a period
    if not dev.endswith('.'):
        dev += '.'

    return dev


@csrf_exempt
def send_email(request):
    if request.method == 'POST':
        # Extract user data from session
        user_id = request.session.get('user_id')

        if user_id is not None:
            try:
                user = GGUser.objects.get(User_ID=user_id)
                email = user.Email
                username = user.Username

                # Debugging output
                print(f"User ID: {user_id}, Username: {username}, Email: {email}")

            except GGUser.DoesNotExist:
                return JsonResponse({'error': 'User not found'})
        else:
            return JsonResponse({'error': 'User not authenticated'})

        # Extract form data
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')

        # Perform any additional validation or processing as needed

        # Construct email message
        email_body = f"User name: {username}\nEmail: {email}\nSubject: {subject}\nMessage: {message}"

        recipient_email = 'gamegeekwebsite@gmail.com'

        sender_email1 = email

        # Construct email message
        try:
            send_mail(subject, email_body, sender_email1, [recipient_email])
            response_data = {'status': 'success',
                             'message': [email, username, subject, email_body, recipient_email, sender_email1]}
        except Exception as e:
            print(f"Error sending email: {e}")
            response_data = {'status': 'error', 'message': 'Error sending email'}

        # Return a JSON response indicating success or failure
        return JsonResponse(response_data)

    # If the form is not valid or the request method is not POST
    return JsonResponse({'status': 'error', 'message': 'Invalid form submission'})


from django.db.models import Case, When, Value, IntegerField
from django.db.models.functions import Cast


def get_order_field(order_by_field, order_direction):
    order_mapping = {
        'Game\'s Name (Alphabetically)': 'Name',
        'Newest Games': '-Original_Release_Date',
        'Oldest Games': 'Original_Release_Date',
        'Highest Age Rating': '-Age_Rating',
        'Lowest Age Rating': 'Age_Rating',
        'Highest Rating Count': '-User_Rating_Count',
        'Lowest Rating Count': 'User_Rating_Count',
        'Highest Rating': '-Average_User_Rating',
        'Lowest Rating': 'Average_User_Rating',
        'Largest Size': '-Size',
        'Smallest Size': 'Size',
        # Add other mappings as needed
    }
    order_field = order_mapping.get(order_by_field, 'Name')
    return '-' + order_field if order_direction == 'desc' else order_field


def annotate_age_rating(queryset):
    age_rating_annotation = Cast(Case(
        When(Age_Rating='4+', then=Value(4)),
        When(Age_Rating='9+', then=Value(9)),
        When(Age_Rating='12+', then=Value(12)),
        When(Age_Rating='17+', then=Value(17)),
        default=Value(0),
        output_field=IntegerField(),
    ), IntegerField())
    return queryset.annotate(numeric_age_rating=age_rating_annotation)


def annotate_rating(queryset):
    average_user_rating_annotation = Cast(Case(
        When(Average_User_Rating='"Inapplicable"', then=Value(0.0)),
        When(Average_User_Rating='1.0', then=Value(1.0)),
        When(Average_User_Rating='1.5', then=Value(1.5)),
        When(Average_User_Rating='2.0', then=Value(2.0)),
        When(Average_User_Rating='2.5', then=Value(2.5)),
        When(Average_User_Rating='3.0', then=Value(3.0)),
        When(Average_User_Rating='3.5', then=Value(3.5)),
        When(Average_User_Rating='4.0', then=Value(4.0)),
        When(Average_User_Rating='4.5', then=Value(4.5)),
        When(Average_User_Rating='5.0', then=Value(5.0)),
        default=Value(-1.0),
        output_field=FloatField(),
    ), FloatField())

    return queryset.annotate(age_rating=average_user_rating_annotation)


def convert_rating_count(value):
    try:
        # Convert to int, handling 'below 5' as a special case
        if value.lower() == 'below 5':
            return 0
        else:
            # Check if the value is in the format 'xxx.0' and convert to int
            return int(float(value))
    except ValueError:
        return 0


def convert_rating(value):
    try:
        # Convert to int, handling 'Inapplicable' as a special case
        if value.lower() == 'inapplicable':
            return 0
        else:
            # Check if the value is in the format 'xxx.0' and convert to int
            return int(float(value))
    except ValueError:
        return 0


def sort_by(request):
    # Default ordering
    user_id = request.session.get('user_id')
    user_age = ''
    user_age_group = 0
    game_queryset = []

    if user_id is not None:
        try:
            user = GGUser.objects.get(User_ID=user_id)
            user_age = user.Approved_age_group

            # Function to extract the numeric part from age group strings
            def extract_numeric_part(age_group):
                match = re.search(r'\d+', age_group)
                if match:
                    return int(match.group())
                return 0

            # Convert user age group string to numerical value
            user_age_group = extract_numeric_part(
                user_age) if user_age and user_age != 'fals' else 12
        except GGUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'})
    else:
        return JsonResponse({'error': 'User not authenticated'})

    # Retrieve objects from the GamesList model suitable for the user's approved age group

    if user_age_group == 17:
        # If the user has the highest age group, retrieve all games
        game_queryset = GamesList.objects.all()
    else:
        # Use Case and When to handle age group comparison
        game_queryset = GamesList.objects.annotate(
            numeric_age_rating=Case(
                When(Age_Rating='4+', then=Value(4)),
                When(Age_Rating='9+', then=Value(9)),
                When(Age_Rating='12+', then=Value(12)),
                When(Age_Rating='17+', then=Value(17)),
                default=Value(0),  # Default case, adjust as needed
                output_field=IntegerField(),
            )
        ).filter(numeric_age_rating__lte=user_age_group)

    order_by_field = request.GET.get('order_by', 'Name')
    order_direction = request.GET.get('order_direction', 'asc')

    # Get the corresponding field for ordering
    order_field = get_order_field(order_by_field, order_direction)

    if order_by_field in ('Newest Games', 'Oldest Games'):
        game_queryset = game_queryset.order_by(order_field)
    elif order_by_field in ('Highest Age Rating', 'Lowest Age Rating'):
        game_queryset = annotate_age_rating(game_queryset)
        order_field = '-numeric_age_rating' if order_by_field == 'Highest Age Rating' else 'numeric_age_rating'
        game_queryset = game_queryset.order_by(order_field)
    elif order_by_field in ('Highest Rating', 'Lowest Rating'):
        order_field = '-age_rating' if order_by_field == 'Highest Rating' else 'age_rating'
        game_queryset = annotate_rating(game_queryset)
        game_queryset = game_queryset.order_by(order_field)

    else:
        # Explicitly handle alphabetical sorting
        if order_direction == 'asc':
            game_queryset = game_queryset.order_by(order_field, 'Name')
        else:
            game_queryset = game_queryset.order_by(f'{order_field}', '-Name')

    # Convert rating count and serialize the queryset to JSON
    games_list = [
        {
            'Name': game.Name,
            'Icon_URL': game.Icon_URL,
            'URL': game.URL,
            'ID': game.ID,
        }
        for game in game_queryset
    ]

    request.session['games_list'] = games_list
    response_data = {
        'message': 'The games are:',
        'order_by_field': order_by_field,
        'order_direction': order_direction,
    }

    return JsonResponse(response_data)


## -----------Extracters  methods --------------------------

@require_http_methods(["GET"])
def ExtractPrice(request):
    games_list = GamesList.objects.all()
    unique_prices = games_list.values_list('Price', flat=True).distinct()
    price_list = list(unique_prices)
    return JsonResponse({'prices': price_list}, safe=False)


@require_http_methods(["GET"])
def ExtractGenre(request):
    games_list = GamesList.objects.all()
    all_genres = [genre.strip() for Genres in games_list.values_list('Genres', flat=True) for genre in
                  Genres.split(',')]
    unique_genere = list(set(all_genres))
    return JsonResponse({'genres': unique_genere}, safe=False)


@require_http_methods(["GET"])
def ExtractLanguage(request):
    games_list = GamesList.objects.all()
    all_languages = [language.strip() for languages in games_list.values_list('Languages', flat=True) for language in
                     languages.split(',')]
    unique_languages = list(set(all_languages))
    return JsonResponse({'languages': unique_languages}, safe=False)


@require_http_methods(["GET"])
def ExtractInAppPurchases(request):
    games_list = GamesList.objects.all()
    unique_InAppPurchase = games_list.values_list('In_app_Purchases', flat=True).distinct()
    InAppPurchases_list = list(unique_InAppPurchase)
    return JsonResponse({'InAppPurchases': InAppPurchases_list}, safe=False)


@require_http_methods(["GET"])
def ExtractRating(request):
    games_list = GamesList.objects.all()
    unique_Rating = games_list.values_list('Average_User_Rating', flat=True).distinct()
    Rating_list = list(unique_Rating)
    return JsonResponse({'Rating': Rating_list}, safe=False)


def filter_games_multiple(request):
    # Extract valid categories from GET parameters
    valid_categories = {'Genres', 'Languages', 'In_app_Purchases', 'Price', 'Average_User_Rating'}
    categories = {key.rstrip('[]') for key in request.GET.keys() if key.rstrip('[]') in valid_categories}
    # extract the age group for the user
    user_id = request.session.get('user_id')
    user_age = ''
    user_age_group = 0
    filtered_games_queryset = []
    filter_status = ''

    if user_id is not None:
        try:
            user = GGUser.objects.get(User_ID=user_id)
            user_age = user.Approved_age_group

            # Function to extract the numeric part from age group strings
            def extract_numeric_part(age_group):
                match = re.search(r'\d+', age_group)
                if match:
                    return int(match.group())
                return 0

            # Convert user age group string to numerical value
            user_age_group = extract_numeric_part(
                user_age) if user_age and user_age != 'fals' else 12
        except GGUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'})
    else:
        return JsonResponse({'error': 'User not authenticated'})

    # Retrieve objects from the GamesList model suitable for the user's approved age group

    if user_age_group == 17:
        # If the user has the highest age group, retrieve all games
        filtered_games_queryset = GamesList.objects.all()
    else:
        # Use Case and When to handle age group comparison
        filtered_games_queryset = GamesList.objects.annotate(
            numeric_age_rating=Case(
                When(Age_Rating='4+', then=Value(4)),
                When(Age_Rating='9+', then=Value(9)),
                When(Age_Rating='12+', then=Value(12)),
                When(Age_Rating='17+', then=Value(17)),
                default=Value(0),  # Default case, adjust as needed
                output_field=IntegerField(),
            )
        ).filter(numeric_age_rating__lte=user_age_group)

    if 'Average_User_Rating' in categories:

        rating_values = request.GET.getlist('Average_User_Rating[]')
        rating_values = [float(value) for value in rating_values if value.isdigit()]
        if rating_values:
            filtered_games_queryset = filtered_games_queryset.filter(Average_User_Rating__in=rating_values)
        else:
            filtered_games_queryset = filtered_games_queryset.filter(Average_User_Rating=5.0)

    if categories:
        # Start with an initial Q object
        q_objects = Q()

        for category in categories:
            values = request.GET.getlist(f'{category}[]')
            category_q = Q()
            for value in values:
                category_q |= Q(**{f'{category}__icontains': value})
            q_objects &= category_q  # Use AND to filter by multiple categories

        # Apply the filtered categories to the queryset
        filtered_games_queryset = filtered_games_queryset.filter(q_objects)
        if len(filtered_games_queryset) == 0:
            filter_status = 'no games satisfies the filter'
    # Convert queryset to a list of dictionaries
    games_list = [
        {
            'Name': game.Name,
            'Icon_URL': game.Icon_URL,
            'URL': game.URL,
            'ID': game.ID,
        }
        for game in filtered_games_queryset
    ]

    request.session['filtered_games'] = games_list
    cache.set('filter_status', filter_status)

    # Include filtered categories in the response
    response_data = {
        'filtered_games': games_list,

    }

    return JsonResponse(response_data, safe=False)


## -----------favourite games methods --------------------------
##------------DELETE SORTED AND FILTERED GAMES----------------##


@csrf_exempt
def add_to_favorites(request, game_id):
    if request.method == 'GET':
        try:
            user_id = request.session.get('user_id')

            # Check if the user exists
            user = GGUser.objects.get(User_ID=user_id)

            # Check if the game exists
            game = GamesList.objects.get(ID=game_id)

            # Check if the game is already in favorites
            if Favorite.objects.filter(User_ID=user, Game_ID=game).exists():
                return JsonResponse({'success': False, 'error': 'Game is already in favorites'})

            # Add the game to favorites
            Favorite.objects.create(User_ID=user, Game_ID=game)

            return JsonResponse({'success': True})

        except GGUser.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User does not exist'})

        except GamesList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Game does not exist'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def favorite_games(request):
    user_id = request.session.get('user_id')
    if user_id:
        user_favorites = Favorite.objects.filter(User_ID=user_id)
        games_data = [{'id': favorite.Game_ID.ID,
                       'icon_url': favorite.Game_ID.Icon_URL,
                       'name': clean_name(favorite.Game_ID.Name),
                       'url': favorite.Game_ID.URL} for favorite in user_favorites]
        return JsonResponse({'games': games_data})
    else:
        return JsonResponse({'error': 'User not authenticated'})


@csrf_exempt
def remove_favorite(request, game_id):
    if request.method == 'GET':
        try:
            user_id = request.session.get('user_id')

            # Check if the user is logged in
            if not user_id:
                return JsonResponse({'success': False, 'error': 'User not logged in'})

            # Check if the game is in the user's favorites
            favorite = Favorite.objects.filter(User_ID=user_id, Game_ID=game_id).first()
            if favorite:
                favorite.delete()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Game not found in favorites'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


## -----------visitied games methods --------------------------

def visited_games(request):
    user_id = request.session.get('user_id')

    if user_id:
        visited_games = Visited.objects.filter(User_ID=user_id)
        games_data = [
            {
                'id': visited_game.Game_ID.ID,
                'name': clean_name(visited_game.Game_ID.Name),
                'url': visited_game.Game_ID.URL,
                'icon_url': visited_game.Game_ID.Icon_URL,
                'visited_date': visited_game.Visited_date.strftime('%Y-%m-%d') if visited_game.Visited_date else None,
            }
            for visited_game in visited_games
        ]
        return JsonResponse({'games': games_data})
    else:
        return JsonResponse({'error': 'User not authenticated'})


from datetime import date


@csrf_exempt
def save_visited_game(request, game_id):
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            user = GGUser.objects.get(User_ID=user_id)
            game = GamesList.objects.get(ID=game_id)

            # Check if the user has already visited this game
            visited_game, created = Visited.objects.get_or_create(User_ID=user, Game_ID=game)

            # If the game is already visited, update the visited date
            if not created:
                # Update the visited date with the current day, month, and year
                today = date.today()
                visited_game.Visited_date = today
                visited_game.save()

            return JsonResponse({'success': True})

        except GGUser.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User does not exist'})

        except GamesList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Game does not exist'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# --------------------recently viewed game -----------------------------
from django.shortcuts import get_object_or_404


def add_to_recently_viewed(request, game_id):
    user_id = request.session.get('user_id')

    if user_id:
        try:
            user = GGUser.objects.get(User_ID=user_id)
            game = get_object_or_404(GamesList, ID=game_id)

            recently_viewed_games = request.session.get('recently_viewed_games', [])

            # Remove the game if it already exists in the list
            if game_id in recently_viewed_games:
                recently_viewed_games.remove(game_id)

            # Add the new game to the list
            recently_viewed_games.insert(0, game_id)

            # Keep only the first 4 unique games while maintaining order
            recently_viewed_games = list(dict.fromkeys(recently_viewed_games))

            # Assign order based on the index
            recently_viewed_games = [
                {"id": game_id, "order": i} for i, game_id in enumerate(recently_viewed_games)
            ]

            # Sort the games based on their order in the session
            recently_viewed_games.sort(key=lambda x: x["order"])

            # Limit the length to 4
            recently_viewed_games = recently_viewed_games[:4]

            request.session['recently_viewed_games'] = [game["id"] for game in recently_viewed_games]
            request.session.modified = True

            return JsonResponse({'success': True})

        except GGUser.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User does not exist'})

        except GamesList.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Game does not exist'})

    return JsonResponse({'success': False, 'error': 'User not authenticated'})


def recently_viewed_games(request):
    user_id = request.session.get('user_id')

    if user_id:
        recently_viewed_game_ids = request.session.get('recently_viewed_games', [])
        recently_viewed_games = GamesList.objects.filter(ID__in=recently_viewed_game_ids)

        # Assign order based on the index
        recently_viewed_games = [
            {"id": game.ID, "order": recently_viewed_game_ids.index(game.ID)}
            for game in recently_viewed_games
        ]

        # Sort the games based on their order in the session
        recently_viewed_games.sort(key=lambda x: x["order"])

        recently_viewed_games_data = [
            {
                'id': game["id"],
                'name': clean_name(GamesList.objects.get(ID=game["id"]).Name),
                'url': GamesList.objects.get(ID=game["id"]).URL,
                'icon_url': GamesList.objects.get(ID=game["id"]).Icon_URL,
            }
            for game in recently_viewed_games
        ]

        return JsonResponse({'games': recently_viewed_games_data})

    return JsonResponse({'error': 'User not authenticated'})


# SignUp Verification

def custom_signup_confirmation_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = GGUser.objects.get(User_ID=uid)
    except (TypeError, ValueError, OverflowError, GGUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.email_confirmed = True
        user.save()

        if request.method == 'POST':
            # Valid token, allow the user to set a new password
            ageGroup = request.POST.get('ageGroup')
            user.Approved_age_group = ageGroup
            user.save()
            return render(request, 'AgeEstimation.html', {'status': 'done', 'message': 'Done'})
        else:
            # Handle GET request, show age group form
            return render(request, 'AgeEstimation.html', {'status': 'done', 'message': 'Done'})

    else:
        error_message = 'Unexpected error occurred, please try again'
        return render(request, 'AgeEstimation.html', {'status': 'error', 'message': error_message})


def custom_signup_confirmation(request):
    print("Debugging ")
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = GGUser.objects.get(User_ID=user_id)
                email = user.Email
                first_name = user.First_name

            except GGUser.DoesNotExist:
                return HttpResponseNotFound('User not found')

        # Generate a token and uid for the user
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        email = user.Email

        # Create the reset link for age group assignment
        reset_link = f"{request.scheme}://{request.get_host()}/verify-signUp/{uid}/{token}/"

        email_message = (
            f'Hi {first_name}, thank you for joining Game Geek\n'
            f'To confirm your registration please click on this link:\n'
            f'{reset_link}'
        )

        # Send the email with the constructed message
        send_mail(
            'Confirm registration',
            email_message,
            'gamegeekwebsite@gmail.com',
            [email],
            fail_silently=False,
        )
        if 'error_message' in request.POST:
            print("Debugging in verify method ")
            return HttpResponse(status=400)
        print("Debugging 1016 ")
        return HttpResponse(status=200)

    return render(request, 'AgeEstimation.html')


def custom_resendConfirmation_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = GGUser.objects.get(User_ID=uid)
    except (TypeError, ValueError, OverflowError, GGUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.email_confirmed = True
        user.save()
        return render(request, 'login.html', {'status': 'successfullyConfirmed', 'message': 'Successfully confirmed'})

    else:
        error_message = 'Unexpected error occurred, please try again'
        return render(request, 'login.html', {'status': 'error', 'message': error_message})


def custom_resendConfirmation(request):
    if request.method == 'POST':
        username = request.POST['username']
        user_id = request.session.get('user_id')
        if user_id:
            try:
                user = GGUser.objects.get(User_ID=user_id)
                email = user.Email
                age_group = user.Approved_age_group
                first_name = user.First_name
            except GGUser.DoesNotExist:
                return HttpResponseNotFound('User not found')

            # Generate a token and uid for the user
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            email = user.Email

            # Create the reset link for confirmation
            reset_link = f"{request.scheme}://{request.get_host()}/resendConfirmation/{uid}/{token}/"

            # Construct the email message
            email_message = (
                f'Hi {user.First_name}, thank you for joining Game Geek.\n'
                f'To confirm your registration, please click on this link:\n'
                f'{reset_link}'
            )

            # Send the email with the constructed message
            send_mail(
                'Confirm registration',
                email_message,
                'gamegeekwebsite@gmail.com',
                [email],
                fail_silently=False,
            )
            return HttpResponse(status=200)

    return render(request, 'login.html')
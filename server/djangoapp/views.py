# Uncomment the required imports before adding the code

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.core.management import call_command
from django.db import connection
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)

DEFAULT_CARS = [
    {"CarModel": "Pathfinder", "CarMake": "Nissan"},
    {"CarModel": "Qashqai", "CarMake": "Nissan"},
    {"CarModel": "XTRAIL", "CarMake": "Nissan"},
    {"CarModel": "A-Class", "CarMake": "Mercedes"},
    {"CarModel": "C-Class", "CarMake": "Mercedes"},
    {"CarModel": "E-Class", "CarMake": "Mercedes"},
    {"CarModel": "A4", "CarMake": "Audi"},
    {"CarModel": "A5", "CarMake": "Audi"},
    {"CarModel": "A6", "CarMake": "Audi"},
    {"CarModel": "Sorrento", "CarMake": "Kia"},
    {"CarModel": "Carnival", "CarMake": "Kia"},
    {"CarModel": "Cerato", "CarMake": "Kia"},
    {"CarModel": "Corolla", "CarMake": "Toyota"},
    {"CarModel": "Camry", "CarMake": "Toyota"},
    {"CarModel": "Kluger", "CarMake": "Toyota"},
]


def _ensure_db_initialized():
    try:
        tables = connection.introspection.table_names()
        if 'djangoapp_carmake' not in tables or 'auth_user' not in tables:
            call_command('migrate', interactive=False)
            initiate()
            if not User.objects.filter(username='root').exists():
                User.objects.create_superuser(
                    'root', 'root@example.com', 'rootpassword'
                )
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    'admin', 'admin@example.com', 'admin123'
                )
    except Exception as e:
        logger.error(f"Error initializing DB: {e}")


# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    _ensure_db_initialized()
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    _ensure_db_initialized()
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    # email_exist = False  # Remove unused variable
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except Exception:  # Use specific exception and remove unused whitespace
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(
            username=username, first_name=first_name,
            last_name=last_name, password=password, email=email
        )
        # Login the user and redirect to the list page
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"username": username, "error": "Already Registered"}
        return JsonResponse(data)


# Method to get the list of cars
def get_cars(request):
    _ensure_db_initialized()
    try:
        count = CarMake.objects.filter().count()
        print(count)
        if count == 0:
            initiate()
        car_models = CarModel.objects.select_related('car_make')
        cars = []
        for car_model in car_models:
            cars.append(
                {
                    "CarModel": car_model.name,
                    "CarMake": car_model.car_make.name
                }
            )
        if cars:
            return JsonResponse({"CarModels": cars})
    except Exception as e:
        logger.error(f"Error in get_cars: {e}")
    return JsonResponse({"CarModels": DEFAULT_CARS})


# Method to get list of dealerships
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    return JsonResponse(
        {"status": 200, "dealers": dealerships})


# Method to view reviews for individual dealer
def get_dealer_reviews(request, dealer_id):
    # If dealer id has been provided
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)

        for review_detail in reviews:
            # Call analyze_review_sentiments
            # check if the response is valid
            response = analyze_review_sentiments(
                review_detail['review'])
            print(response)

            if response is not None and 'sentiment' in response:
                review_detail['sentiment'] = response['sentiment']
            else:
                # If there's no sentiment, default to 'neutral'
                review_detail['sentiment'] = 'neutral'

        return JsonResponse({"status": 200, "reviews": reviews})

    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create an `add_review` view to submit a review
def add_review(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        print(data)  # Log the incoming data for debugging
        try:
            response = post_review(data)
            if response.get("status") == 200:
                print("Review posted successfully:", response)
            return JsonResponse(
                {
                    "status": 200,
                    "message": "Review posted successfully",
                    "review": data
                })
        except Exception as e:
            print(f"Error in posting review: {e}")
            return JsonResponse(
                {
                    "status": 401,
                    "message": "Error in posting review"
                })
    else:
        return JsonResponse(
            {
                "status": 403,
                "message": "Unauthorized"
            })

from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import os
from django.conf import settings
from .models import ApiKey , UserSignup, Room, Message, UserInvoices
from django.utils import timezone


api_key = " "
app_id = " "

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        # Retrieve the form data from the request
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if a user with the provided email already exists
        if UserSignup.objects.filter(email=email).exists():
            return JsonResponse({'message': 'The email provided is already in use'})

        # Check if password and confirm_password match
        if password != confirm_password:
            return JsonResponse({'message': 'Passwords do not match'})

        # Create a new UserSignup object
        user_signup = UserSignup(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            confirm_password=confirm_password,
        )

        # Save the UserSignup object to the database
        user_signup.save()

        # Create a consumer for the newly signed-up user
        try:
            # Define the API endpoint URL
            url = "https://unify.apideck.com/vault/consumers"


            # Define the headers
            headers = {
                "x-apideck-app-id": app_id,
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            # Define the request body with the obtained consumer_id
            request_body = {
                "consumer_id": user_signup.user_id,
                # Add other fields or data as needed
            }

            # Make the POST request
            response = requests.post(url, headers=headers, json=request_body)

            # Check the response status code
            if response.status_code == 200:
                return JsonResponse({'message': 'Signup successful'})
            else:
                # If consumer creation fails, you might want to delete the UserSignup object to rollback the signup
                user_signup.delete()
                return JsonResponse({'error': f'Failed to create consumer. Status code: {response.status_code}'}, status=400)

        except Exception as e:
            # If an error occurs, you might want to delete the UserSignup object to rollback the signup
            user_signup.delete()
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    # If the request method is not POST
    return JsonResponse({'message': 'Invalid request'})


# Handle Log in
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = UserSignup.objects.get(email=email)
            if user.password == password:
                # Correct login details
                url = "/users/"
                user_id = user.user_id
                return JsonResponse({'url': url, 'user_id': user_id})
            else:
                # Incorrect password
                return JsonResponse({'error': 'Incorrect login details'})
        except UserSignup.DoesNotExist:
            # User not found
            return JsonResponse({'error': 'Incorrect login details'})

    return JsonResponse({'error': 'Invalid Request'})



# @csrf_exempt
# def create_consumer(request):
#     if request.method == "POST":
#         try:
#             # Get the consumer_id from the request data
#             consumer_id = request.POST.get("consumer_id")

#             if not consumer_id:
#                 return JsonResponse({"error": "consumer_id is required in the request data."}, status=400)

#             # Define the API endpoint URL
#             url = "https://unify.apideck.com/vault/consumers"



#             # Define the headers
#             headers = {
#                 "x-apideck-app-id": app_id,
#                 "Authorization": f"Bearer {api_key}",
#                 "Content-Type": "application/json",
#             }

#             # Define the request body with the obtained consumer_id
#             request_body = {
#                 "consumer_id": consumer_id,
#                 # Add other fields or data as needed
#             }

#             # Make the POST request
#             response = requests.post(url, headers=headers, json=request_body)

#             # Check the response status code
#             if response.status_code == 200:
#                 return JsonResponse({"message": "Consumer created successfully"})
#             else:
#                 return JsonResponse({"error": f"Failed to create consumer. Status code: {response.status_code}"}, status=400)

#         except Exception as e:
#             return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

#     return JsonResponse({"error": "Only POST requests are allowed for this endpoint."}, status=405)


# @csrf_exempt
# def create_connection(request):
#     if request.method == "POST":
#         # Get the POST parameters from the request
#         service_id = request.POST.get("service_id")
#         unified_api = request.POST.get("unified_api")
#         user_id = request.POST.get("user_id")



#         # Define the URL template
#         url_template = "https://unify.apideck.com/vault/connections/{unified_api}/{service_id}"

#         # Define the headers
#         headers = {
#             "x-apideck-app-id": app_id,
#             "x-apideck-consumer-id": user_id,
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json",
#         }

#         # Fill in the URL template with path parameters
#         url = url_template.format(unified_api=unified_api, service_id=service_id)

#         # Make the POST request
#         response = requests.post(url, headers=headers)

#         # Check the response status code
#         if response.status_code == 201:
#             return JsonResponse({"message": "Connection created successfully"})
#         else:
#             return JsonResponse({"error": f"Failed to create connection. Status code: {response.status_code}"}, status=400)
#     else:
#         return JsonResponse({"error": "Only POST requests are allowed"}, status=405)



# @csrf_exempt
# def authorize_connection(request):
#     # Get the parameters from the GET request
#     unified_api = request.GET.get("unified_api")
#     service_id = request.GET.get("service_id")
#     user_id = request.GET.get("user_id")

#     # Define the API endpoint URL
#     url = "https://unify.apideck.com/vault/sessions"


#     # Define the headers with your API key and other required parameters
#     headers = {
#         "x-apideck-app-id": app_id,
#         "x-apideck-consumer-id": user_id,
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json"
#     }

#     # Make the POST request
#     response = requests.post(url, headers=headers)

#     # Check the response status code
#     if response.status_code == 200:
#         # Session created successfully, parse the JSON response
#         session_data = response.json()["data"]
#         session_token = session_data["session_token"]

#         # Construct the URL
#         redirect_url = f"https://vault.apideck.com/integrations/{unified_api}/{service_id}?jwt={session_token}"

#         return JsonResponse({"redirect_url": redirect_url})
#     else:
#         # Handle error cases here
#         return JsonResponse({"error": f"Error: {response.status_code}"}, status=500)


@csrf_exempt
def create_authorize_connection(request):
    if request.method == "POST":
        # Connection creation logic

        # Get the POST parameters from the request
        service_id = request.POST.get("service_id")
        unified_api = request.POST.get("unified_api")
        user_id = request.POST.get("user_id")




        # Define the URL template
        url_template = "https://unify.apideck.com/vault/connections/{unified_api}/{service_id}"

        # Define the headers
        headers = {
            "x-apideck-app-id": app_id,
            "x-apideck-consumer-id": user_id,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Fill in the URL template with path parameters
        url = url_template.format(unified_api=unified_api, service_id=service_id)

        # Make the POST request
        response = requests.post(url, headers=headers)

        # Check the response status code
        if response.status_code == 201:
            # Authorization logic

            # Define the API endpoint URL for authorization
            auth_url = "https://unify.apideck.com/vault/sessions"

            # Make the POST request for authorization
            auth_response = requests.post(auth_url, headers=headers)

            # Check the response status code for authorization
            if auth_response.status_code == 200:
                # Session created successfully, parse the JSON response
                session_data = auth_response.json()["data"]
                session_token = session_data["session_token"]

                # Construct the URL
                redirect_url = f"https://vault.apideck.com/integrations/{unified_api}/{service_id}?jwt={session_token}"

                return JsonResponse({"message": "Connection and authorization successful", "redirect_url": redirect_url})
            else:
                # Handle error cases for authorization
                return JsonResponse({"error": f"Authorization error: {auth_response.status_code}"}, status=500)
        else:
            # Handle error cases for connection creation
            return JsonResponse({"error": f"Failed to create connection. Status code: {response.status_code}"}, status=400)
    elif request.method == "GET":
        return JsonResponse({"error": "GET requests are not supported for this endpoint"}, status=405)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)



# Create a new room
@csrf_exempt
def create_room(request):
    try:
        # Extract user_id from URL query parameters
        user_id = request.GET.get('user_id')

        # Find the user
        user = UserSignup.objects.get(user_id=user_id)

        # Create a new room
        new_room = Room.objects.create(room_name="New Room")

        # Return the room_id as JSON response
        return JsonResponse({'room_id': new_room.room_id})

    except UserSignup.DoesNotExist:
        return JsonResponse({'response': 'User not found.'}, status=404)
    except Exception as e:
        error_message = f"Error creating room: {str(e)}"
        return JsonResponse({'response': error_message}, status=500)



@csrf_exempt
def get_all_invoices(request):
    # Get the consumer_id parameter from the GET request
    user_id = request.GET.get("user_id")

    # Define the API endpoint URL
    url = "https://unify.apideck.com/accounting/invoices"


    # Define the headers with your API key and other required parameters
    headers = {
        "x-apideck-app-id": app_id,
        "x-apideck-consumer-id": user_id,  # Use the consumer ID from the request
        "Authorization": f"Bearer {api_key}",
    }

    # Make the GET request
    response = requests.get(url, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        # Invoices retrieved successfully, parse the JSON response
        invoice_data = response.json()
        invoices = invoice_data["data"]

        return JsonResponse({"invoices": invoices})

    else:
        # Handle error cases here
        return JsonResponse({"error": f"Error: {response.status_code}"}, status=500)


import json
from .apikey import apikey
os.environ['OPENAI_API_KEY'] = apikey
from langchain.llms import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from langchain.agents import create_json_agent
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.llms.openai import OpenAI
from langchain.tools.json.tool import JsonSpec


# chat with JSON data
@csrf_exempt
def chat_with_json(request):
    try:
        # Extract user_question and json_data from request body
        user_question = request.POST.get('user_question')
        json_data = request.POST.get('json_data')

        if not user_question or not json_data:
            return JsonResponse({'response': 'Invalid request. Missing user_question or json_data.'})

        # Convert JSON string to Python dictionary
        json_data = json.loads(json_data)


        openai_api_key = apikey

        json_spec = JsonSpec(dict_=json_data, max_value_length=4000)
        json_toolkit = JsonToolkit(spec=json_spec)

        json_agent_executor = create_json_agent(llm=OpenAI(temperature=0), toolkit=json_toolkit, verbose=True)

        # Run the agent
        response = json_agent_executor.run(user_question)

        return JsonResponse({'response': response})

    except Exception as e:
        error_message = f"Error processing request: {str(e)}"
        print(error_message)
        return JsonResponse({'response': 'Request not completed, try again.'}, status=500)


from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import requests
from langchain.agents import create_json_agent
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.llms import OpenAI
from langchain.llms.openai import OpenAI
from langchain.tools.json.tool import JsonSpec


# # Endpoint to get invoices, create a room, and store in session
# @csrf_exempt
# def invoices_store_in_session(request):
#     try:
#         # Get the user_id parameter from the GET request
#         user_id = request.GET.get("user_id")

#         # Create a new room
#         new_room = Room.objects.create(room_name="New Room")

#         # Return the room_id as part of the JSON response
#         response_data = {"room_id": new_room.room_id}

#         # Define the API endpoint URL
#         url = "https://unify.apideck.com/accounting/invoices"


#         # Define the headers with your API key and other required parameters
#         headers = {
#             "x-apideck-app-id": app_id,
#             "x-apideck-consumer-id": user_id,  # Use the consumer ID from the request
#             "Authorization": f"Bearer {api_key}",
#         }

#         # Make the GET request
#         response = requests.get(url, headers=headers)

#         # Check the response status code
#         if response.status_code == 200:
#             # Invoices retrieved successfully, parse the JSON response
#             invoice_data = response.json()
#             invoices = invoice_data["data"]

#             # Store the invoices in the session
#             request.session['invoices'] = invoices

#             # Add the room_id to the response data
#             response_data["response"] = "Invoices stored in session successfully"

#             return JsonResponse(response_data)
#         else:
#             # Handle error cases here
#             return JsonResponse({"response": f"Error: {response.status_code}"}, status=500)

#     except UserSignup.DoesNotExist:
#         return JsonResponse({'response': 'User not found.'}, status=404)
#     except Exception as e:
#         error_message = f"Error processing request: {str(e)}"
#         print(error_message)
#         return JsonResponse({'response': 'Request not completed, try again.'}, status=500)


@csrf_exempt
def invoices_store_in_database(request):
    try:
        user_id = request.GET.get("user_id")

        new_room = Room.objects.create(room_name="New Room")

        response_data = {"room_id": new_room.room_id}

        url = "https://unify.apideck.com/accounting/invoices"
        headers = {
            "x-apideck-app-id": app_id,
            "x-apideck-consumer-id": user_id,
            "Authorization": f"Bearer {api_key}",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            invoice_data = response.json()
            invoices = invoice_data["data"]

            current_user = UserSignup.objects.get(user_id=user_id)

            # Store invoices in the database
            user_invoices, created = UserInvoices.objects.get_or_create(user=current_user)
            user_invoices.invoices_data = invoices
            user_invoices.save()

            response_data["response"] = "Invoices stored in the database successfully"

            return JsonResponse(response_data)
        else:
            return JsonResponse({"response": f"Error: {response.status_code}"}, status=500)

    except UserSignup.DoesNotExist:
        return JsonResponse({'response': 'User not found.'}, status=404)
    except Exception as e:
        error_message = f"Error processing request: {str(e)}"
        print(error_message)
        return JsonResponse({'response': 'Request not completed, try again.'}, status=500)


# Endpoint to chat about invoices
@csrf_exempt
def chat_about_invoices(request):
    try:
        user_question = request.POST.get('user_question')
        room_id = request.POST.get('room_id')
        user_id = request.POST.get("user_id")

        if not user_question or not room_id:
            return JsonResponse({'response': 'Invalid request. Missing user_question or room_id.'})

        # Fetch invoices from the database
        try:
            current_user = UserSignup.objects.get(user_id=user_id)
            user_invoices = UserInvoices.objects.get(user=current_user)
            invoices = user_invoices.invoices_data
        except UserInvoices.DoesNotExist:
            # If not found, fetch invoices again and store in the database
            url = "https://unify.apideck.com/accounting/invoices"
            headers = {
                "x-apideck-app-id": app_id,
                "x-apideck-consumer-id": user_id,
                "Authorization": f"Bearer {api_key}",
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                invoice_data = response.json()
                invoices = invoice_data["data"]

                # Store invoices in the database
                UserInvoices.objects.create(user=request.user, invoices_data=invoices)
            else:
                return JsonResponse({"response": f"Error fetching invoices: {response.status_code}"}, status=500)


        room = Room.objects.get(room_id=room_id)

        # Save the prompt
        message = Message(content=user_question, agent_response=False,
                           room=room, created_on=timezone.now())
        message.save()


        # Continue with your chat logic using user_question and invoices data
        openai_api_key = apikey
        json_spec = JsonSpec(dict_={"invoices": invoices}, max_value_length=4000)
        json_toolkit = JsonToolkit(spec=json_spec)
        json_agent_executor = create_json_agent(llm=OpenAI(temperature=0), toolkit=json_toolkit, verbose=True)

        # Run the agent
        response = json_agent_executor.run(user_question)

        # Save the response in the Message model
        if response:
            message = Message(content=response, agent_response=True, room=room, created_on=timezone.now())
            message.save()

        return JsonResponse({'response': response})

    except Room.DoesNotExist:
        return JsonResponse({'response': 'Room not found.'}, status=404)
    except Exception as e:
        error_message = f"Error processing request: {str(e)}"
        print(error_message)
        return JsonResponse({'response': error_message}, status=500)






@csrf_exempt
def get_room_messages(request):
    try:
        # Get the user_id and room_id from the GET parameters
        room_id = request.GET.get('room_id')

        # Get the room
        try:
            room = Room.objects.get(room_id=room_id)
        except Room.DoesNotExist:
            return JsonResponse({'error': 'Room not found'}, status=404)

        # Retrieve messages for the room
        messages = Message.objects.filter(room=room).order_by('-created_on')
        message_data = [
            {
                'message_id': message.message_id,
                'content': message.content,
                'agent_response': message.agent_response,
                'created_on': message.created_on
            }
            for message in messages
        ]

        # Return the room messages as JSON response
        return JsonResponse({'Messages': message_data})

    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)


from django.shortcuts import render,redirect
from .forms import CSVUploadForm

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from .models import Company, CSVFile, ApiKey , UserSignup, Room, Message
from .serializers import CSVFileSerializer
from django.http import HttpResponse
from dotenv import load_dotenv
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
import os
from django.http import HttpResponseServerError
from django.conf import settings
import json
from django.core.exceptions import ObjectDoesNotExist
import uuid

'''
@csrf_exempt
def save_user_id(request):
    if request.method == 'POST':
        user_id = request.GET.get('user_id')

        try:
            # Check if the user_id already exists
            existing_user = UserSignup.objects.filter(user_id=user_id).first()

            if existing_user:
                # user_id already exists, return an appropriate response
                return JsonResponse({'message': 'user_id already exists.'}, status=400)
            else:
                # Create a new UserSignup instance
                new_user = UserSignup(user_id=user_id)
                new_user.save()

                # Return a success response
                return JsonResponse({'message': 'user_id saved successfully.'})

        except Exception as e:
            error_message = f"Error saving user_id: {str(e)}"
            print(error_message)
            return JsonResponse({'message': error_message}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method.'}, status=400)
'''

# Signup view
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

        # Return a JSON response indicating successful signup
        return JsonResponse({'message': 'Signup successful'})

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


# Create Company API
@api_view(['POST'])
@csrf_exempt
def create_company(request):
    user_id = request.query_params.get('user_id')
    print(user_id)
    company_name = request.POST.get('company')
    print(company_name)

    # Check if user_id is present
    if not user_id:
        return Response({'message': 'User ID is missing.'}, status=400)

    try:
        # Find the user associated with the user_id
        user = UserSignup.objects.get(user_id=user_id)

        # Check if a company with the same name already exists
        existing_company = Company.objects.filter(company_name=company_name, created_by=user_id)
        if existing_company.exists():
            return Response({'message': 'Company with the same name already exists.'})

        # Create the company with the associated user
        company = Company(company_name=company_name, created_by=user)
        company.save()

        message = f"Company {company.company_name} created successfully!"

        return Response({'message': message, 'status' : 'Success'})

    except UserSignup.DoesNotExist:
        return Response({'message': 'User not found.'}, status=404)
    except Exception as e:
        return Response({'message': f'Error creating company: {str(e)}'}, status=500)

'''
@api_view(['POST'])
@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.cleaned_data['company']
            file = form.cleaned_data['file']
            metadata = form.cleaned_data['metadata']

            # Save the file to a desired location
            file_path = handle_uploaded_file(file)

            # Create a new CSVFile instance and save it to the database
            try:
                company = Company.objects.get(company=company)
                csv_file = CSVFile(company=company, file=file_path, metadata=metadata)
                csv_file.save()
                #return redirect('', company=company)
            except Exception as e:
                error_message = f"Error saving CSV file: {e}"
                print(error_message)
                return HttpResponseServerError(error_message)
        else:
            error_message = f"Invalid form data: {form.errors}"
            print(error_message)
            return HttpResponseServerError(error_message)
    else:
        form = CSVUploadForm()

    companies = Company.objects.all()
    return render(request, 'companies/upload.html', {'form': form, 'companies': companies})
'''

# Get user companies, drop down menu in frontend

@api_view(['GET'])
@csrf_exempt
def get_user_companies(request):
    user_id = request.GET.get('user_id')
    try:
        user = UserSignup.objects.get(user_id=user_id)
        companies = Company.objects.filter(created_by=user)
        company_data = [{'company_name': company.company_name, 'company_id': company.company_id}
                        for company in companies]

        return JsonResponse({'companies': company_data})
    except UserSignup.DoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)
    except Exception as e:
        error_message = f"Error retrieving companies: {str(e)}"
        print(error_message)
        return JsonResponse({'message': error_message}, status=500)



# upload CSV file

# Function to check if a file name already exists for the given company
def is_file_name_unique(company, file_name):
    return not CSVFile.objects.filter(company_id=company.company_id,
                                       file=os.path.join(settings.MEDIA_ROOT, file_name)).exists()

# upload CSV file
@api_view(['POST'])
@csrf_exempt
def upload_csv_file(request):
    if request.method == 'POST':
        user_id = request.query_params.get('user_id')
        company_name = request.POST.get('company')
        file = request.FILES.get('file')
        description = request.POST.get('description')

        try:
            # Find the user
            user = UserSignup.objects.get(user_id=user_id)

            # Find the company instance based on the user and company name
            company = Company.objects.get(created_by=user, company_name=company_name)

            # Check if the file name is unique for the company
            if not is_file_name_unique(company, file.name):
                return JsonResponse({'message': 'A file with the same name already exists for this company.'}, status=400)

            # Save the file to a desired location
            file_path = handle_uploaded_file(file)

            # Create a new CSVFile instance and save it to the database
            csv_file = CSVFile(company_id=company.company_id, file=file_path, description=description)
            csv_file.save()

            return JsonResponse({'message': 'CSV file uploaded successfully.'})
        except UserSignup.DoesNotExist:
            return JsonResponse({'message': 'User not found.'}, status=404)
        except Company.DoesNotExist:
            return JsonResponse({'message': 'Company not found.'}, status=404)
        except Exception as e:
            error_message = f"Error saving CSV file: {str(e)}"
            print(error_message)
            return JsonResponse({'message': error_message}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method.'}, status=400)

# Function to handle uploaded file
def handle_uploaded_file(file):
    if file is not None:
        # Save the uploaded file to the 'media' directory with the original file name
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)

        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return file_path
    else:
        raise ValueError("No file provided.")


# Get all files for a company created-as paths to be used by AI agent
@csrf_exempt
def get_csv_files(request):
    try:
        user_id = request.GET.get('user_id')
        company_name = request.POST.get('company_name')
        print("Request Data:", request.POST)
        print("user_id:", user_id)
        print("company_name:", company_name)

        # Find the user
        user = UserSignup.objects.get(user_id=user_id)
        print(user.user_id)

        # Find the company instance based on the user and company name
        company = Company.objects.get(created_by=user.user_id, company_name=company_name)
        print(company)

        csv_files = company.csv_files.all()
        file_paths = [csv_file.file.path for csv_file in csv_files]
        file_info = inspect_user_csv(file_paths)

        return JsonResponse({'file_info': file_info})


        #return JsonResponse({'file_paths': file_paths})


    except UserSignup.DoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)
    except Company.DoesNotExist:
        return JsonResponse({'message': 'Company not found.'}, status=404)
    except Exception as e:
        error_message = f"Error retrieving CSV files: {str(e)}"
        print(error_message)
        return JsonResponse({'message': error_message}, status=500)


# Inspect csv files
import pandas as pd
from django.http import JsonResponse

def inspect_user_csv(file_paths):
    data = {}

    for file_path in file_paths:
        try:
            # Read the CSV file using pandas
            df = pd.read_csv(file_path)

            # Get the file name from the path
            file_name = file_path.split('\\')[-1]  # For Windows use file_path.split('\\')[-1]

            # If the CSV file has multiple worksheets, extract the column names for each sheet
            if isinstance(df, dict):
                worksheet_names = list(df.keys())
                worksheet_columns = {file_name: {worksheet_name: df[worksheet_name].columns.tolist()} for worksheet_name in worksheet_names}
                data.update(worksheet_columns)
            else:
                # If the CSV file has only one worksheet, extract the column names directly
                data[file_name] = df.columns.tolist()

        except Exception as e:
            error_message = f"Error processing file '{file_path}': {str(e)}"
            print(error_message)
            data[file_path] = error_message

    return data


# View all csv files for a company- Send to frontend
import os
@csrf_exempt
def get_csv_names(request):
    try:
        user_id = request.GET.get('user_id')
        company_name = request.POST.get('company_name')
        print("Request Data:", request.POST)
        print("user_id:", user_id)
        print("company_name:", company_name)

        # Find the user
        user = UserSignup.objects.get(user_id=user_id)
        print(user.user_id)

        # Find the company instance based on the user and company name
        company = Company.objects.get(created_by=user.user_id, company_name=company_name)
        print(company)

        csv_files = company.csv_files.all()
        file_data = [{'file_name': os.path.basename(csv_file.file.name), 'description': csv_file.description}
                     for csv_file in csv_files]

        return JsonResponse({'file_data': file_data})

    except UserSignup.DoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)
    except Company.DoesNotExist:
        return JsonResponse({'message': 'Company not found.'}, status=404)
    except Exception as e:
        error_message = f"Error retrieving CSV names: {str(e)}"
        print(error_message)
        return JsonResponse({'message': error_message}, status=500)


'''

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        user_question = request.POST.get('user_question')
        user_csv = request.FILES.get('user_csv')

        # Save the uploaded CSV file to a location accessible by the csvapp script
         # Save the uploaded CSV file to a specific directory
        file_directory = os.path.join(settings.MEDIA_ROOT, 'csv_files')  # Modify 'csv_files' to your desired directory name
        os.makedirs(file_directory, exist_ok=True)
        file_path = os.path.join(file_directory, user_csv.name)
        with open(file_path, 'wb') as f:
            for chunk in user_csv.chunks():
                f.write(chunk)

        # Create the CSV agent
        agent = create_csv_agent(OpenAI(), file_path, verbose=True)

        # Get the response from the agent
        response = agent.run(user_question)

        return render(request, 'companies/chat.html', {'response': response})

    return render(request, 'companies/chat.html')

'''

from django.shortcuts import get_object_or_404

@csrf_exempt
def create_room(request):
    try:
        # Extract user_id from URL query parameters
        user_id = request.GET.get('user_id')
        company_name = request.GET.get('company_name')
        print("user_id:", user_id)
        print("company_name:", company_name)

        # Find the user
        user = UserSignup.objects.get(user_id=user_id)
        print("user:", user)

        # Find the company instance based on the user and company name
        company = Company.objects.get(created_by=user, company_name=company_name)
        print("company:", company)

        # Create a new room for the company
        new_room = Room.objects.create(
            room_name="New Room",
            company=company
        )
        print("new_room:", new_room)

        # Return the room_id as JSON response
        return JsonResponse({'room_id': new_room.room_id})

    except UserSignup.DoesNotExist:
        return JsonResponse({'response': 'User not found.'}, status=404)
    except Company.DoesNotExist:
        return JsonResponse({'response': 'Company not found.'}, status=404)
    except Exception as e:
        error_message = f"Error creating room: {str(e)}"
        print(error_message)
        return JsonResponse({'response': error_message}, status=500)

load_dotenv()

from langchain.prompts import PromptTemplate

def create_room_name(prompt):
    api_key_instance = ApiKey.objects.first()
    if api_key_instance:
        openai_api_key = api_key_instance.api_key
    else:
        return JsonResponse({'response': 'No API key found.'})

    llm= OpenAI(OpenAI(openai_api_key=openai_api_key, temperature=0.0))
    # Create a templates
    title_template= PromptTemplate(
        input_variables=['topic'],
        template='write me a short prompt title about {prompt}')
    title_chain=llm(llm=llm, prompt=title_template, verbose=True,output_key='title')
    if prompt:
        title = title_chain.run(prompt)
        print('AI gen title: ', title)
    return title


from django.utils import timezone
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType

# chat with csv
@csrf_exempt
def chat_with_csv(request):
    try:
        # Extract room_id from request POST data
        room_id = request.POST.get('room_id')
        if not room_id:
            return JsonResponse({'response': 'Room ID not found in the request.'})

        # Extract user_id and company_name from URL query parameters
        user_id = request.GET.get('user_id')
        company_name = request.GET.get('company_name')

        # Extract prompt from request body
        prompt = request.POST.get('prompt')

        # Save the prompt in the Message model
        if prompt:
            print("prompt:", prompt)
            room = Room.objects.get(room_id=room_id)
            print(" first room:", room)

        # Find the user
        user = UserSignup.objects.get(user_id=user_id)

        # Find the company instance based on the user and company name
        company = Company.objects.get(created_by=user, company_name=company_name)

        csv_files = company.csv_files.all()
        file_paths = [csv_file.file.path for csv_file in csv_files]

        # Load the OpenAI API key from the apikey model
        api_key_instance = ApiKey.objects.first()

        if api_key_instance:
            openai_api_key = api_key_instance.api_key
        else:
            return JsonResponse({'response': 'No API key found.'})

        # Process CSV files
        openai_api_key = openai_api_key
        print("file_paths :",  file_paths)
        print("Open ai key :",  openai_api_key)


        if file_paths:
            # Create the CSV agent
            csv_agent = create_csv_agent(OpenAI(openai_api_key = openai_api_key,
                                                 temperature=0),
                                         file_paths, verbose=True)

            # Get the response from the agent
            user_question = prompt

            # Save the prompt
            message = Message(content=prompt, agent_response=False,
                               room=room, created_on=timezone.now())
            message.save()

            if user_question:
                response = csv_agent.run(user_question)

                # Save the response in the Message model
                if response:
                    room = Room.objects.get(room_id=room_id)
                    message = Message(content=response,
                                        agent_response=True, room=room, created_on=timezone.now())
                    message.save()

                    return JsonResponse({'response': response})

        # Return a default response if no CSV files are found
        return JsonResponse({'response': 'No CSV files found.'})

    except UserSignup.DoesNotExist:
        return JsonResponse({'response': 'User not found.'}, status=404)
    except Company.DoesNotExist:
        return JsonResponse({'response': 'Company not found.'}, status=404)
#    except Exception as e:
#        error_message = f"Error processing request: {str(e)}"
#        print(error_message)
#        return JsonResponse({'response': 'Request not completed, try again.'}, status=500)


from django.core.exceptions import ValidationError


# Room List API
@csrf_exempt
def room_list(request):
    try:
        # Get the user_id and company_name from the URL parameters
        user_id = request.GET.get('user_id')
        company_name = request.GET.get('company_name')

        # Get the UserSignup object based on the user_id parameter from the URL
        user = get_object_or_404(UserSignup, user_id=user_id)

        # Get the Company object based on the company_name parameter from the URL
        company = get_object_or_404(Company, company_name=company_name, created_by=user)

        # Get the Company ID
        company_id = company.company_id

        # Get the rooms for the specified company
        rooms = Room.objects.filter(company__company_id=company_id)

        # Extract the room names from the rooms queryset
        room_names = [room.room_name for room in rooms]

        # Return the room names as JSON response
        return JsonResponse({'room_names': room_names})

    except ValidationError as e:
        return JsonResponse({'error': 'Validation Error', 'message': str(e)}, status=400)

    except UserSignup.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    except Company.DoesNotExist:
        return JsonResponse({'error': 'Company not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)



# Display messages when a room is opened in frontend
@csrf_exempt
def room_messages(request):
    try:
        # Get the user_id and room_id from the GET parameters
        user_id = request.GET.get('user_id')
        room_id = request.GET.get('room_id')

        # Check if the user_id exists in the UserSignup model
        try:
            user = UserSignup.objects.get(user_id=user_id)
        except UserSignup.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        # Get the room associated with the user's company
        try:
            room = Room.objects.get(room_id=room_id, company__created_by=user)
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
        return JsonResponse({room.room_id: message_data})

    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)

# Rename room API
@csrf_exempt
def rename_room(request):
    try:
        # Get the user_id, company_name, room_id, and new_room_name from the POST parameters
        user_id = request.GET.get('user_id')
        company_name = request.GET.get('company_name')
        room_id = request.POST.get('room_id')
        new_room_name = request.POST.get('new_room_name')

        # Get the UserSignup object based on the user_id parameter from the POST data
        user = get_object_or_404(UserSignup, user_id=user_id)

        # Get the Company object based on the company_name parameter from the POST data
        company = get_object_or_404(Company, company_name=company_name, created_by=user)

        # Get the Room object to be renamed based on the room_id parameter from the POST data
        room = get_object_or_404(Room, room_id=room_id, company=company)

        # Rename the room
        room.room_name = new_room_name
        room.save()

        # Return a success JSON response
        return JsonResponse({'message': f'Room renamed successfully'})

    except ValidationError as e:
        return JsonResponse({'error': 'Validation Error', 'message': str(e)}, status=400)

    except UserSignup.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    except Company.DoesNotExist:
        return JsonResponse({'error': 'Company not found'}, status=404)

    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)

# Delete Room API

@csrf_exempt
def delete_room(request):
    try:
        # Get the user_id, company_name, and room_id from the POST parameters
        user_id = request.GET.get('user_id')
        company_name = request.GET.get('company_name')
        room_id = request.GET.get('room_id')

        # Get the UserSignup object based on the user_id parameter from the POST data
        user = get_object_or_404(UserSignup, user_id=user_id)

        # Get the Company object based on the company_name parameter from the POST data
        company = get_object_or_404(Company, company_name=company_name, created_by=user)

        # Get the Room object to be deleted based on the room_id parameter from the POST data
        room = get_object_or_404(Room, room_id=room_id, company=company)

        # Delete the room
        room.delete()

        # Return a success JSON response
        return JsonResponse({'message': f'Room {room.room_name} deleted successfully'})

    except ValidationError as e:
        return JsonResponse({'error': 'Validation Error', 'message': str(e)}, status=400)

    except UserSignup.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    except Company.DoesNotExist:
        return JsonResponse({'error': 'Company not found'}, status=404)

    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error', 'message': str(e)}, status=500)



# Delete csv
from django.core.files import File
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

# Function to delete a CSV file
def delete_csv_file(csv_file):
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, str(csv_file.file))
        print("Deleting file:", file_path)

        if os.path.exists(file_path):
            # Delete the file
            os.remove(file_path)

        # Delete the CSVFile instance
        csv_file.delete()
    except Exception as e:
        error_message = f"Error deleting CSV file: {str(e)}"
        print(error_message)


# Function to get file descriptions for a given list of file names
def get_file_descriptions(company, file_names):
    file_descriptions = {}
    for file_name in file_names:
        file_name = file_name.strip()
        print("File name:", file_name)

        # Find the corresponding CSVFile instance
        csv_file = CSVFile.objects.filter(company=company, file__endswith=file_name).first()

        if csv_file:
            file_descriptions[file_name] = csv_file.description

    return file_descriptions




# View to delete CSV files and return file descriptions
@csrf_exempt
def delete_csv_files(request):
    try:
        user_id = request.GET.get('user_id')
        company_name = request.POST.get('company_name')
        file_names = request.POST.getlist('file_names[]')

        user = UserSignup.objects.get(user_id=user_id)
        company = Company.objects.get(created_by=user, company_name=company_name)

        deleted_files = []
        not_found_files = []

        for file_name in file_names:
            file_name = file_name.strip()
            print("File name:", file_name)

            # Find the corresponding CSVFile instance
            csv_file = CSVFile.objects.filter(company=company, file__endswith=file_name).first()

            if csv_file:
                # Delete the file and the CSVFile instance
                delete_csv_file(csv_file)
                deleted_files.append(file_name)
            else:
                not_found_files.append(file_name)

        # Get file descriptions for the deleted files
        file_descriptions = get_file_descriptions(company, deleted_files)

        response_data = {
            'message': 'CSV files deleted successfully.',
            'deleted_files': [{'file_name': file_name, 'description': file_descriptions.get(file_name, "")}
                              for file_name in deleted_files],
            'not_found_files': not_found_files
        }

        return JsonResponse(response_data)

    except UserSignup.DoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)
    except Company.DoesNotExist:
        return JsonResponse({'message': 'Company not found.'}, status=404)
    except Exception as e:
        error_message = f"Error deleting CSV files: {str(e)}"
        print(error_message)
        return JsonResponse({'message': error_message}, status=500)


# Save and update API key
@csrf_exempt
def update_api_key(request):
    if request.method == 'POST':
        api_key = request.POST.get('api_key')  # Retrieve the API key from the request data

        # Fetch the existing API key instance
        api_key_instance = ApiKey.objects.first()

        if api_key_instance:
            # Update the API key value
            api_key_instance.api_key = api_key
            api_key_instance.save()

            return JsonResponse({'message': 'API key updated successfully.'})
        else:
            # Create a new API key instance
            ApiKey.objects.create(api_key=api_key)

            return JsonResponse({'message': 'API key created successfully.'})

    return JsonResponse({'message': 'Invalid request method.'})

# Delete api key api
def delete_api_key(request):
    if request.method == 'POST':
        api_key_value = request.POST.get('api_key')

        # Look for the API key instance
        try:
            api_key = ApiKey.objects.get(api_key=api_key_value)
        except ApiKey.DoesNotExist:
            return JsonResponse({'message': 'API key not found.'}, status=404)

        # Update the status to inactive
        api_key.status = False
        api_key.save()

        return JsonResponse({'message': 'API key deleted successfully.'})

    return JsonResponse({'message': 'Invalid request method.'})



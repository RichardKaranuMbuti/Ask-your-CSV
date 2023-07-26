from django.shortcuts import render,redirect
from .forms import CSVUploadForm

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from .models import Company, CSVFile, ApiKey , UserSignup
from .serializers import CSVFileSerializer
from django.http import HttpResponse
from dotenv import load_dotenv
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
import os
from django.http import HttpResponseServerError
from django.conf import settings
import json
from django.core.exceptions import ObjectDoesNotExist
import uuid

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
            return JsonResponse({'message': 'User with this email already exists'})

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
                url = f"/user/{user.user_id}/"  # URL with user ID
                return JsonResponse({'url': url})
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

        return Response({'message': 'Company created successfully!',
                          'company_id': company.company_id,
                          'company_name': company.company_name,
                         })
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

        return JsonResponse({'file_paths': file_paths})

    except UserSignup.DoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)
    except Company.DoesNotExist:
        return JsonResponse({'message': 'Company not found.'}, status=404)
    except Exception as e:
        error_message = f"Error retrieving CSV files: {str(e)}"
        print(error_message)
        return JsonResponse({'message': error_message}, status=500)


# View all csv files for a company- Send to frontend
import os

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


load_dotenv()

# Chat with csv
@csrf_exempt
def chat_with_csv(request):
    try:
        # Extract user_id and company_name from URL query parameters
        user_id = request.GET.get('user_id')
        company_name = request.GET.get('company_name')  # Use GET instead of POST
        print(user_id)
        print(company_name)

        # Extract prompt from request body
        prompt = request.POST.get('prompt')

        print("prompt:", prompt)

        # Fetch CSV files using the company ID

        # Find the user
        user = UserSignup.objects.get(user_id=user_id)
        print("user:", user)

        # Find the company instance based on the user and company name
        company = Company.objects.get(created_by=user, company_name=company_name)
        print("company:", company)

        csv_files = company.csv_files.all()
        file_paths = [csv_file.file.path for csv_file in csv_files]
        print("file_paths:", file_paths)

        # Load the OpenAI API key from the apikey model
        api_key_instance = ApiKey.objects.first()

        if api_key_instance:
            openai_api_key = api_key_instance.api_key
        else:
            return JsonResponse({'response': 'No API key found.'})

        # Process CSV files
        if file_paths:
            agent = create_csv_agent(OpenAI(openai_api_key=openai_api_key), file_paths, verbose=True)
            user_question = prompt
            print(user_question)

            if user_question:
                print("user question: ", user_question)
                response = agent.run(user_question)
                print(response)

            # Return the response as JSON
            return JsonResponse({'response': response})

        # Return a default response if no CSV files are found
        return JsonResponse({'response': 'No CSV files found.'})

    except UserSignup.DoesNotExist:
        return JsonResponse({'response': 'User not found.'}, status=404)
    except Company.DoesNotExist:
        return JsonResponse({'response': 'Company not found.'}, status=404)
    except Exception as e:
        error_message = f"Error processing request: {str(e)}"
        print(error_message)
        return JsonResponse({'response': error_message}, status=500)

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



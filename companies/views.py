from django.shortcuts import render,redirect
from .forms import CSVUploadForm

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from .models import Company, CSVFile, ApiKey
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




@api_view(['POST'])
@csrf_exempt
def create_company(request):
    name = request.data.get('company')

    # Check if a company with the same name already exists
    if Company.objects.filter(company=name).exists():
        return Response({'message': 'Company with the same name already exists.'}, status=400)

    try:
        company = Company.objects.create(company=name)
        return Response({'message': 'Company created successfully!'})
    except Exception as e:
        return Response({'message': f'Error creating company: {str(e)}'}, status=500)


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

@api_view(['POST'])
@csrf_exempt
def upload_csv_file(request):
    if request.method == 'POST':
        company = request.POST.get('company')
        file = request.FILES.get('file')
        metadata = request.POST.get('metadata')

        # Save the file to a desired location
        file_path = handle_uploaded_file(file)

        try:
            # Find the company instance
            company_instance = Company.objects.get(company=company)

            # Create a new CSVFile instance and save it to the database
            csv_file = CSVFile(company=company_instance, file=file_path, metadata=metadata)
            csv_file.save()

            return Response({'message': 'CSV file uploaded successfully.'})
        except Company.DoesNotExist:
            return Response({'message': 'Company not found.'}, status=404)
        except Exception as e:
            error_message = f"Error saving CSV file: {str(e)}"
            print(error_message)
            return Response({'message': error_message}, status=500)
    else:
        return Response({'message': 'Invalid request method.'}, status=400)

def handle_uploaded_file(file):
    if file is not None:
        # Save the uploaded file to the 'media' directory
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)

        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return file_path
    else:
        raise ValueError("No file provided.")


# Get all files for a company
def get_csv_files(request, company_id):
    try:
        company = Company.objects.get(pk=company_id)
        csv_files = company.csv_files.all()

        file_paths = [csv_file.file.path for csv_file in csv_files]

        return file_paths
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Company not found.'}, status=404)
    except FileNotFoundError as e:
        return JsonResponse({'error': str(e)}, status=404)

# View all csv files for a company
@api_view(['GET'])
@csrf_exempt
def get_csv_files_list(request, company_id):
    try:
        company = Company.objects.get(pk=company_id)
        csv_files = company.csv_files.all()

        if csv_files:
            file_paths = [csv_file.file.path for csv_file in csv_files]
            return Response({'csv_files': file_paths})
        else:
            return Response({'message': 'No CSV files found for this company.'})
    except Company.DoesNotExist:
        return Response({'message': 'Company not found.'}, status=404)

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

@csrf_exempt
def chat_with_csv(request, company_id):
    # Fetch prompt from the request (assuming it's sent as a JSON payload)
    prompt = json.loads(request.body)['prompt']

    # Load the OpenAI API key from the apikey model
    api_key_instance = ApiKey.objects.first()
    
    if api_key_instance:
        openai_api_key = api_key_instance.api_key
        
    else:
        return JsonResponse({'response': 'No API key found.'})

    # Fetch CSV files using the company ID
    file_paths = get_csv_files(request, company_id)

    # Process CSV files
    if file_paths:
        agent = create_csv_agent(OpenAI(openai_api_key=openai_api_key), file_paths, verbose=True)
        user_question = prompt

        if user_question:
            response = agent.run(user_question)
            print(response)

        # Return the response as JSON
        return JsonResponse({'response': response})

    # Return a default response if no CSV files are found
    return JsonResponse({'response': 'No CSV files found.'})


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


# Delete Company API
@csrf_exempt
def delete_company(request, company_id):
    if request.method == 'POST':

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return JsonResponse({'message': 'Company not found.'}, status=404)

        # Update the active field to False
        company.active = False
        company.save()

        return JsonResponse({'message': 'Company deleted successfully.'})


    return JsonResponse({'message': 'Invalid request method.'})


# Delete csv file 
@api_view(['POST'])
@csrf_exempt
def delete_csv_file(request, company_id):
    company = Company.objects.get(pk=company_id)

    # Get the file path from the request
    file_path = request.POST.get('file_path')

    try:
        # Find the CSV file associated with the company and file path
        csv_file = CSVFile.objects.get(company=company, file_path=file_path)

        # Delete the file from the filesystem
        if os.path.exists(csv_file.file_path):
            os.remove(csv_file.file_path)

        # Delete the CSV file instance
        csv_file.delete()

        return Response({'message': 'CSV file deleted successfully.'})
    except CSVFile.DoesNotExist:
        return Response({'message': 'CSV file not found.'}, status=404)
    except Exception as e:
        return Response({'message': str(e)}, status=500)
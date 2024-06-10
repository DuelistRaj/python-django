from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import UploadFileForm
from .models import UploadedFile
from django.conf import settings
import pandas as pd
import openpyxl
import json
import os

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if there's already an xlsx file present
            media_path = settings.MEDIA_ROOT + '/uploads'
            existing_files = [f for f in os.listdir(media_path) if f.endswith('.xlsx')]
            if existing_files:
                # Delete existing xlsx file(s)
                for file in existing_files:
                    os.remove(os.path.join(media_path, file))
            form.save()
            return redirect('display_last_file')
    else:
        form = UploadFileForm()
    return render(request, 'raciapp/upload.html', {'form': form})


def display_last_file(request):
    try:
        # Get the latest uploaded file
        uploaded_file = UploadedFile.objects.latest('id')
    except ObjectDoesNotExist:
        # Handle the case where no file is found
        return render(request, 'raciapp/display.html', {'error_message': 'No file found.'})

    # Open the file and get the data
    wb = openpyxl.load_workbook(uploaded_file.file.path)
    sheet = wb.active
    rows = sheet.iter_rows(values_only=True)
    data = list(rows)

    return render(request, 'raciapp/display.html', {'data': data, 'file_name': uploaded_file.file.name})

def save_changes(request):
    if request.method == 'POST' and request.accepts('application/json'):
        # Parse the JSON data from the request body
        data = json.loads(request.body)

        # Extract the data
        data_rows = data['data']

        # Convert to DataFrame
        df = pd.DataFrame(data_rows, columns=['ID', 'SepalLength', 'SepalWidth', 'PetalLength', 'PetalWidth', 'Species'])

        # Define the Excel writer using xlsxwriter engine
        excel_writer = pd.ExcelWriter(r'C:\Users\Dueli\OneDrive\Documents\python-django\raci\media\uploads\yrdy.xlsx', engine='xlsxwriter')

        # Write DataFrame to Excel sheet
        df.to_excel(excel_writer, index=False, sheet_name='Sheet1')

        # Close the Excel writer
        excel_writer.close()

        # Return success response
        return JsonResponse({'status': 'success'})
    else:
        # Return error response if method is not POST or client does not accept JSON
        return JsonResponse({'status': 'error'}, status=400)
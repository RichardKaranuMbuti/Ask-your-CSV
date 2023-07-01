from django.contrib import admin

# Register your models here.
from companies.models import Company, CSVFile

admin.site.register(Company)
admin.site.register(CSVFile)

from django.contrib import admin

# Register your models here.
from companies.models import Company, CSVFile, ApiKey

admin.site.register(Company)
admin.site.register(CSVFile)
admin.site.register(ApiKey)
from django.contrib import admin

# Register your models here.
from companies.models import Company, CSVFile, ApiKey , UserSignup, Room, Message

admin.site.register(Company)
admin.site.register(CSVFile)
admin.site.register(ApiKey)
admin.site.register(UserSignup)
admin.site.register(Room)
admin.site.register(Message)
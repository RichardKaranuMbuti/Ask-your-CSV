from django.db import models
import string
import random
from django.urls import reverse
from django.utils import timezone

# Create your models here.

class UserSignup(models.Model):
    user_id = models.CharField(max_length=20, primary_key=True)
    created_on = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_on = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_id}"

# Company Model
class Company(models.Model):
    company_id = models.CharField(max_length=8, primary_key=True)
    company_name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(UserSignup, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.company_id:
            self.company_id = self.generate_company_id()
        super().save(*args, **kwargs)

    def generate_company_id(self):
        digits = ''.join(random.choices(string.digits, k=5))
        letters = ''.join(random.choices(string.ascii_letters, k=3))
        return digits + letters

    def __str__(self):
        return f"{self.company_name}: {self.active}"
    

# CSv Model
class CSVFile(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='csv_files', default='DEFAULT')
    file = models.FileField(upload_to='csv_files/')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.company.company_name} - {self.file.name}"


    
# API model
class ApiKey(models.Model):
    api_key = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.api_key


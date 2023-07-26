from django.db import models
import string
import random
from django.urls import reverse
from django.utils import timezone
import random
import string
# Create your models here.

# User Model
class UserSignup(models.Model):
    user_id = models.CharField(max_length=13, unique=True, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    confirm_password = models.CharField(max_length=128, default='')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.user_id:
            # Generate a 13-character user_id with a mix of 7 numbers and 6 letters
            numbers = ''.join(random.choices(string.digits, k=7))
            letters = ''.join(random.choices(string.ascii_letters, k=6))
            user_id_list = list(numbers + letters)
            random.shuffle(user_id_list)
            user_id = ''.join(user_id_list)

            # Check if the generated user_id already exists in the database
            while UserSignup.objects.filter(user_id=user_id).exists():
                random.shuffle(user_id_list)
                user_id = ''.join(user_id_list)

            self.user_id = user_id

        super(UserSignup, self).save(*args, **kwargs)

        
'''
class UserSignup(models.Model):
    user_id = models.CharField(max_length=50, primary_key=True)
    created_on = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_on = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_id}"
'''
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


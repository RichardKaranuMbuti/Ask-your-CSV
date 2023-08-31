from django.db import models
import string
import random
from django.urls import reverse
from django.utils import timezone
import random
import string
# Create your models here.

# Password recovery model
class PasswordRecovery(models.Model):
    email = models.EmailField(null=False)
    code =  models.IntegerField(null=False)
    created_on = models.DateTimeField(auto_now_add=True)

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
        numbers = ''.join(random.choices(string.digits, k=5))
        letters = ''.join(random.choices(string.ascii_letters, k=3))
        company_id_list = list(numbers + letters)
        random.shuffle(company_id_list)
        company_id = ''.join(company_id_list)
        return company_id

    def __str__(self):
        return f"{self.company_name}: {self.active}"
    
import os
# CSv Model
class CSVFile(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='csv_files', default='DEFAULT')
    file = models.FileField(upload_to='csv_files/')
    description = models.TextField(blank=True)

    def __str__(self):
        file_name = os.path.basename(self.file.name)
        return f"{self.company.company_name} - {self.company.created_by} - {file_name}"


    
# API model
class ApiKey(models.Model):
    api_key = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.api_key



# Rooms Model
class Room(models.Model):
    room_id = models.CharField(max_length=8, primary_key=True)
    room_name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.room_id:
            self.room_id = self.generate_room_id()
        super().save(*args, **kwargs)

    def generate_room_id(self):
        numbers = ''.join(random.choices(string.digits, k=5))
        letters = ''.join(random.choices(string.ascii_letters, k=3))
        room_id_list = list(numbers + letters)
        random.shuffle(room_id_list)
        room_id = ''.join(room_id_list)
        return room_id

    def __str__(self):
        return self.room_name
    
   
# Messages Model
class Message(models.Model):
    message_id = models.CharField(max_length=8, primary_key=True)
    content = models.TextField()
    agent_response = models.BooleanField(default=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.message_id:
            self.message_id = self.generate_message_id()
        super().save(*args, **kwargs)

    def generate_message_id(self):
        numbers = ''.join(random.choices(string.digits, k=5))
        letters = ''.join(random.choices(string.ascii_letters, k=3))
        message_id_list = list(numbers + letters)
        random.shuffle(message_id_list)
        message_id = ''.join(message_id_list)
        return message_id

    def __str__(self):
        return f'{self.room} + {self.content[0:20]}'

    

from django.db import models

# Create your models here.

class Company(models.Model):
    company = models.CharField(max_length=100)  # Rename the field to 'company'
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.company
    
    class Meta:
        app_label = 'companies'


class CSVFile(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='csv_files')
    file = models.FileField(upload_to='csv_files/')
    metadata = models.TextField(blank=True)

    def __str__(self):
        return f"{self.company.company} - {self.file.name}"
    

class ApiKey(models.Model):
    api_key = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.api_key
from rest_framework import serializers
from .models import CSVFile, PasswordRecovery

class CSVFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVFile
        fields = '__all__'

class PasswordRecoverySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PasswordRecovery
        fields=('pk','email', 'code','created_on')
        depth=1
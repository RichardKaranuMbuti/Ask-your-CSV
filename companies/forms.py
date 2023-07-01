from django import forms
from .models import Company

class CSVUploadForm(forms.Form):
    company = forms.ModelChoiceField(queryset=Company.objects.all(), empty_label=None)
    file = forms.FileField()
    metadata = forms.CharField(max_length=100, required=False)

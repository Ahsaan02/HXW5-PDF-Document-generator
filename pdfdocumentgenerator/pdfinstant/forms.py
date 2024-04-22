from django import forms
from django.core.exceptions import ValidationError

class CSVUploadForm(forms.Form):
    file = forms.FileField(label='Upload CSV file')
    
    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith('.csv'):
            raise ValidationError('Only CSV files are allowed.')
        return file

class ZipFileForm(forms.Form):
    file = forms.FileField()
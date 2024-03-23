from django import forms

class CSVUploadForm(forms.Form):
    file = forms.FileField(label='Upload CSV file')

class ZipFileForm(forms.Form):
    file = forms.FileField()
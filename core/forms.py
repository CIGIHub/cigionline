from django import forms


class Think7AbstractUploadForm(forms.Form):
    file = forms.FileField()

from django import forms
from django.core.exceptions import ValidationError


def validate_file_size(file):
    max_size_in_mb = 10
    if file.size > max_size_in_mb * 1024 * 1024:
        raise ValidationError(f"File size must not exceed {max_size_in_mb} MB.")


class Think7AbstractUploadForm(forms.Form):
    file = forms.FileField(
        required=True,
        label="File",
        widget=forms.ClearableFileInput(attrs={"required": "required", "accept": ".pdf, .doc, .docx"}),
        validators=[validate_file_size]
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"required": "required"}),
    )

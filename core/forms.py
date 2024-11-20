from django import forms


class Think7AbstractUploadForm(forms.Form):
    file = forms.FileField(
        required=True,
        label="File",
        widget=forms.ClearableFileInput(attrs={"required": "required"}),
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"required": "required"}),
    )

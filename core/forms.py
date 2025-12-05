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


CIGI_EVENT_SPACE_CHOICES = [
    ("auditorium", "Auditorium"),
    ("main_foyer", "Main Foyer"),
    ("multipurpose", "Multipurpose Room"),
    ("other", "Other"),
]


class FacilityRentalInquiryForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=100, widget=forms.TextInput(attrs={"autocomplete": "given-name"}))
    last_name = forms.CharField(label="Last Name", max_length=100, widget=forms.TextInput(attrs={"autocomplete": "family-name"}))
    email = forms.EmailField(label="Email Address", widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    phone = forms.CharField(label="Phone Number", max_length=50, widget=forms.TextInput(attrs={"autocomplete": "tel"}))

    company = forms.CharField(label="Company/ Organization Name", max_length=200, widget=forms.TextInput(attrs={"autocomplete": "organization"}))
    org_mission = forms.CharField(label="Organization Mission", widget=forms.Textarea)
    other_orgs = forms.CharField(label="Other Organizations to be Involved in Event", widget=forms.Textarea)

    street = forms.CharField(label="Street Address", max_length=200, widget=forms.TextInput(attrs={"autocomplete": "street-address"}))
    city_province = forms.CharField(label="City & Province", max_length=200, widget=forms.TextInput(attrs={"autocomplete": "address-level2"}))
    postal_code = forms.CharField(label="Postal Code", max_length=20, widget=forms.TextInput(attrs={"autocomplete": "postal-code"}))

    event_title = forms.CharField(label="Event Full Title", max_length=250)
    purpose = forms.CharField(label="Purpose of the Event", widget=forms.Textarea)

    start_date = forms.DateField(label="Event Start Date", widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(label="Event End Date", widget=forms.DateInput(attrs={"type": "date"}))
    start_time = forms.TimeField(label="Event Start Time", widget=forms.TimeInput(attrs={"type": "time"}))
    end_time = forms.TimeField(label="Event End Time", widget=forms.TimeInput(attrs={"type": "time"}))

    space = forms.MultipleChoiceField(label="What CIGI Event Space are you interested in", choices=CIGI_EVENT_SPACE_CHOICES, widget=forms.CheckboxSelectMultiple, required=True)
    attendees = forms.IntegerField(label="Number of Attendees", min_value=1)

    details = forms.CharField(label="Additional Details", widget=forms.Textarea)

    can_provide_liability = forms.BooleanField(
        label="I confirm we can provide a $2M liability certificate before the event",
        required=False,
    )
    liability_contact_if_cannot = forms.CharField(
        label="If you cannot provide this, please include contact info we should reach out to",
        required=False,
        widget=forms.Textarea,
    )

    # Simple honeypot
    website = forms.CharField(label="Website", required=False, widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1", "style": "position:absolute;left:-9999px;"}))

    def clean(self):
        cleaned = super().clean()

        if cleaned.get("website"):  # honeypot trip
            raise ValidationError("Submission blocked.")

        if not cleaned.get("can_provide_liability") and not cleaned.get("liability_contact_if_cannot"):
            self.add_error("liability_contact_if_cannot",
                           "Please provide a contact if you cannot provide the liability certificate.")
        return cleaned

    def clean_space(self):
        values = self.cleaned_data.get("space") or []
        if not values:
            raise forms.ValidationError("Select at least one space.")
        return values

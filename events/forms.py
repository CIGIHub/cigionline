from wagtail.contrib.forms.utils import get_field_clean_name
from django import forms
from django.core.exceptions import ValidationError
from .models import _split_slugs, _match


class HoneypotMixin:
    hp_field = "website"  # classic honeypot name

    def clean(self):
        cleaned = super().clean()
        if cleaned.get(self.hp_field):
            raise forms.ValidationError("Invalid submission.")
        return cleaned


def validate_file_size(file):
    max_size_in_mb = 10
    if file.size > max_size_in_mb * 1024 * 1024:
        raise ValidationError(f"File size must not exceed {max_size_in_mb} MB.")


class EventSubmissionForm(forms.Form):
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


WAGTAIL_FIELD_MAP = {
    'singleline': forms.CharField,
    'multiline': forms.CharField,
    'email': forms.EmailField,
    'number': forms.DecimalField,
    'url': forms.URLField,
    'checkbox': forms.BooleanField,
    'checkboxes': forms.MultipleChoiceField,
    'dropdown': forms.ChoiceField,
    'radio': forms.ChoiceField,
    'date': forms.DateField,
    'datetime': forms.DateTimeField,
    'file': forms.FileField,
}


def build_dynamic_form(event, reg_type, invite=None):
    """
    Build a dynamic Form class from RegistrationFormField rules (no admin/panels tricks).
    """
    fields = []

    # Person basics first
    email_initial = invite.email if getattr(invite, "email", None) else None

    # first_name
    fields.append(("first_name", forms.CharField(label="First name", required=True)))
    # last_name
    fields.append(("last_name", forms.CharField(label="Last name", required=True)))
    # email
    email_field = forms.EmailField(label="Email", required=True, initial=email_initial)
    if email_initial:
        email_field.widget.attrs["readonly"] = "readonly"  # visual lock; we'll enforce server-side too
    fields.append(("email", email_field))

    current_slug = reg_type.slug

    for ff in event.form_fields.all().order_by("sort_order"):
        vis_slugs = _split_slugs(ff.visible_type_slugs)
        if not _match(ff.visible_rule, vis_slugs, current_slug):
            continue

        req_slugs = _split_slugs(ff.required_type_slugs)
        is_required = bool(ff.required) or _match(ff.required_rule, req_slugs, current_slug)

        clean_name = get_field_clean_name(ff.label)
        FieldClass = WAGTAIL_FIELD_MAP.get(ff.field_type, forms.CharField)
        kwargs = {"label": ff.label, "help_text": ff.help_text, "required": is_required}

        if ff.field_type in ("dropdown", "radio", "checkboxes"):
            choices = [(x.strip(), x.strip()) for x in ff.choices.splitlines() if x.strip()]
            kwargs["choices"] = choices
            if ff.field_type == "checkboxes":
                kwargs["widget"] = forms.CheckboxSelectMultiple
            if ff.field_type == "radio":
                kwargs["widget"] = forms.RadioSelect

        if ff.field_type == "multiline":
            kwargs["widget"] = forms.Textarea

        fields.append((clean_name, FieldClass(**kwargs)))

    # Honeypot (off-screen in template CSS, but keep it a real input)
    fields.append((
        HoneypotMixin.hp_field,
        forms.CharField(required=False, label="Leave this field blank",
                        widget=forms.TextInput(attrs={"autocomplete": "off"})),
    ))

    # Build a concrete Form
    return type("EventDynamicForm", (HoneypotMixin, forms.Form), dict(fields))

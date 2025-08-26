from wagtail.contrib.forms.utils import get_field_clean_name
from django import forms
from django.core.exceptions import ValidationError


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
    fields = []

    person_fields = [
        ('first_name', forms.CharField(label="First name")),
        ('last_name', forms.CharField(label="Last name")),
        ('email', forms.EmailField(label="Email")),
    ]
    # Optional: pre-fill/lock email from invite
    if invite and invite.email:
        def locked_email_field():
            f = forms.EmailField(label="Email", initial=invite.email, disabled=True)
            return ('email', f)
        person_fields[2] = locked_email_field()

    fields.extend(person_fields)

    for ff in event.form_fields.all().order_by('sort_order'):
        show_list = ff.show_for_types.all()
        required_list = ff.required_for_types.all()

        visible = (show_list.count() == 0) or show_list.filter(pk=reg_type.pk).exists()
        if not visible:
            continue

        clean_name = get_field_clean_name(ff.label)
        FieldClass = WAGTAIL_FIELD_MAP.get(ff.field_type, forms.CharField)

        kwargs = {
            'label': ff.label,
            'help_text': ff.help_text,
            'required': ff.required or required_list.filter(pk=reg_type.pk).exists(),
        }
        if ff.field_type in ('dropdown', 'radio', 'checkboxes'):
            choices = [(x.strip(), x.strip()) for x in ff.choices.splitlines() if x.strip()]
            kwargs['choices'] = choices
            if ff.field_type == 'checkboxes':
                kwargs['widget'] = forms.CheckboxSelectMultiple
            if ff.field_type == 'radio':
                kwargs['widget'] = forms.RadioSelect
        if ff.field_type == 'multiline':
            kwargs['widget'] = forms.Textarea

        fields.append((clean_name, FieldClass(**kwargs)))

    return type('EventDynamicForm', (forms.Form,), dict(fields))

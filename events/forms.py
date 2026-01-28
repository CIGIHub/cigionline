from wagtail.contrib.forms.utils import get_field_clean_name
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import _split_slugs, _match

BASE_INPUT_CLASS = "cigi-input"
BASE_SELECT_CLASS = "cigi-select"
BASE_GROUP_CLASS = "cigi-group"       # radios/checkbox groups
BASE_FILE_CLASS = "cigi-file-input"
BASE_DATE_CLASS = "cigi-date-input"  # date + datetime
ERROR_CLASS = "has-errors"


def _parse_exts(text: str) -> list[str]:
    # normalize: "pdf, docx, png" -> ["pdf","docx","png"]
    return [t.lower().lstrip(".") for t in (text or "").replace(" ", "").split(",") if t]


def _max_size_validator(max_mb: int):
    def _v(f):
        if f.size > max_mb * 1024 * 1024:
            raise ValidationError(f"File too large. Max size is {max_mb} MB.")
    return _v


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
    'multiselect': forms.MultipleChoiceField,
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
    conditional_rules = []

    email_initial = invite.email if getattr(invite, "email", None) else None

    fields.append(("first_name", forms.CharField(label="First Name", required=True)))
    fields.append(("last_name", forms.CharField(label="Last Name", required=True)))
    email_field = forms.EmailField(label="Email", required=True, initial=email_initial)
    if email_initial:
        email_field.widget.attrs["readonly"] = "readonly"
    fields.append(("email", email_field))

    current_slug = reg_type.slug

    fields_qs = event.registration_form_template.fields.all()

    for ff in fields_qs.order_by("sort_order"):
        vis_slugs = _split_slugs(ff.visible_type_slugs)
        if not _match(ff.visible_rule, vis_slugs, current_slug):
            continue

        req_slugs = _split_slugs(ff.required_type_slugs)
        is_required = bool(ff.required) or _match(ff.required_rule, req_slugs, current_slug)

        key = f"f_{ff.field_key}"
        FieldClass = WAGTAIL_FIELD_MAP.get(ff.field_type, forms.CharField)
        kwargs = {"label": ff.label, "help_text": ff.help_text, "required": is_required}

        if ff.field_type in ("dropdown", "radio", "checkboxes", "multiselect", "date", "datetime", "file"):
            choices = [(x.strip(), x.strip()) for x in ff.choices.splitlines() if x.strip()]
            if ff.field_type == "dropdown":
                choices = [("", "Select an option…")] + choices
            kwargs["choices"] = choices
            if ff.field_type == "checkboxes":
                kwargs["widget"] = forms.CheckboxSelectMultiple()
            if ff.field_type == "radio":
                kwargs["widget"] = forms.RadioSelect()
            if ff.field_type == "multiselect":
                kwargs["widget"] = forms.SelectMultiple()
            if ff.field_type == "date":
                kwargs["widget"] = forms.DateInput(attrs={"type": "date"})
                kwargs.pop("choices", None)  # DateField does not take choices
            if ff.field_type == "datetime":
                kwargs["widget"] = forms.DateTimeInput(attrs={"type": "datetime-local"})
                kwargs.pop("choices", None)  # DateTimeField does not take choices
            if ff.field_type == "file":
                kwargs["widget"] = forms.ClearableFileInput()
                kwargs.pop("choices", None)
                validators = []
                exts = _parse_exts(getattr(ff, "file_allowed_types", ""))
                if exts:
                    validators.append(FileExtensionValidator(allowed_extensions=exts))
                if ff.file_max_mb:
                    validators.append(_max_size_validator(ff.file_max_mb))
                if validators:
                    kwargs["validators"] = validators

        if ff.field_type == "multiline":
            kwargs["widget"] = forms.Textarea()

        if ff.field_type == "conditional_text":
            base = f"f_{ff.field_key}"
            needs_key = f"{base}__enabled"
            details_key = f"{base}__details"
            details_label = ff.conditional_details_label.strip() if getattr(ff, "conditional_details_label", "") else "Please specify"
            details_help = getattr(ff, "conditional_details_help_text", "") or ""

            needs_field = forms.BooleanField(
                label=ff.label,
                required=False,
                help_text=ff.help_text,
            )
            needs_field.widget.attrs["class"] = BASE_INPUT_CLASS
            needs_field.widget.attrs["data-conditional-toggle"] = "1"
            needs_field.widget.attrs["data-conditional-target"] = details_key
            needs_field.widget.attrs["data-conditional-question"] = ff.label
            needs_field.widget.attrs["data_conditional_checkbox_label"] = (
                ff.conditional_label.strip() if getattr(ff, "conditional_label", "") else "Yes"
            )

            details_field = forms.CharField(
                label=details_label,
                required=False,  # enforced conditionally in clean()
                help_text=details_help,
                widget=forms.Textarea(attrs={
                    "rows": 3,
                    "class": BASE_INPUT_CLASS,
                    "data-conditional-details-for": needs_key,
                }),
            )

            fields.append((needs_key, needs_field))
            fields.append((details_key, details_field))

            conditional_rules.append({
                "needs_key": needs_key,
                "details_key": details_key,
                "details_required": bool(getattr(ff, "conditional_details_required", True)),
                "error": f"{details_label}: this field is required.",
            })
            continue
        if ff.field_type == "conditional_dropdown_other":
            base_key = f"f_{ff.field_key}"
            select_key = base_key
            other_key = f"{base_key}__other"

            choices = [(x.strip(), x.strip()) for x in ff.choices.splitlines() if x.strip()]
            choices = [("", "Select an option…")] + choices

            other_value = (getattr(ff, "conditional_other_value", "") or "").strip() or "Other"
            other_label = (getattr(ff, "conditional_other_label", "") or "").strip() or "Please specify"
            other_help = getattr(ff, "conditional_other_help_text", "") or ""
            other_required = bool(getattr(ff, "conditional_other_required", True))

            select_field = forms.ChoiceField(
                label=ff.label,
                required=is_required,
                help_text=ff.help_text,
                choices=choices,
            )
            select_field.widget.attrs["class"] = f"{BASE_SELECT_CLASS}".strip()

            select_field.widget.attrs["data-conditional-select"] = "1"
            select_field.widget.attrs["data-conditional-target"] = other_key
            select_field.widget.attrs["data-conditional-trigger-value"] = other_value

            other_field = forms.CharField(
                label=other_label,
                required=False,
                help_text=other_help,
                widget=forms.TextInput(attrs={"class": BASE_INPUT_CLASS}),
            )

            other_field.widget.attrs["data-conditional-details-for"] = select_key

            fields.append((select_key, select_field))
            fields.append((other_key, other_field))

            conditional_rules.append({
                "kind": "select_other",
                "select_key": select_key,
                "other_key": other_key,
                "trigger_value": other_value,
                "other_required": other_required,
                "error": "Please specify.",
            })
            continue
        field_obj = FieldClass(**kwargs)

        # Add consistent CSS classes to the widget (so templates can stay simple)
        w = field_obj.widget
        cls = w.attrs.get("class", "")

        if ff.field_type in ("dropdown",):
            w.attrs["class"] = f"{cls} {BASE_SELECT_CLASS}".strip()
        elif ff.field_type in ("multiselect",):
            w.attrs["class"] = f"{cls} {BASE_SELECT_CLASS} {BASE_SELECT_CLASS}--multiple".strip()
        elif ff.field_type in ("radio", "checkboxes"):
            # Applies to the group container and/or subwidgets (Django assigns to each subwidget)
            w.attrs["class"] = f"{cls} {BASE_GROUP_CLASS}".strip()
        elif ff.field_type in ("date", "datetime"):
            w.attrs["class"] = f"{cls} {BASE_INPUT_CLASS} {BASE_DATE_CLASS}".strip()
        elif ff.field_type == "file":
            w.attrs["class"] = f"{cls} {BASE_FILE_CLASS}".strip()
        else:
            # default text-ish
            w.attrs["class"] = f"{cls} {BASE_INPUT_CLASS}".strip()

        fields.append((key, field_obj))

    # Honeypot (off-screen in template CSS, but keep it a real input)
    fields.append((
        HoneypotMixin.hp_field,
        forms.CharField(required=False, label="website",
                        widget=forms.TextInput(attrs={"autocomplete": "off"})),
    ))

    attrs = dict(fields)
    attrs["__module__"] = __name__

    DynamicForm = type("EventDynamicForm", (HoneypotMixin, forms.Form), attrs)

    def _dynamic_clean(self):
        cleaned = super(DynamicForm, self).clean()

        for rule in conditional_rules:
            if rule.get("kind") == "select_other":
                selected = (cleaned.get(rule["select_key"]) or "").strip()
                other = (cleaned.get(rule["other_key"]) or "").strip()

                if selected == rule["trigger_value"]:
                    if rule["other_required"] and not other:
                        self.add_error(rule["other_key"], rule["error"])
                else:
                    cleaned[rule["other_key"]] = ""
                continue
            enabled = bool(cleaned.get(rule["needs_key"]))
            details = (cleaned.get(rule["details_key"]) or "").strip()

            if enabled and rule["details_required"] and not details:
                self.add_error(rule["details_key"], "Please specify.")
            if not enabled:
                cleaned[rule["details_key"]] = ""

        return cleaned

    DynamicForm.clean = _dynamic_clean
    return DynamicForm

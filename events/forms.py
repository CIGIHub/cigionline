from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import _split_slugs, _match

NON_ANSWER_FIELD_TYPES = {"rich_text"}
CHOICE_LIMIT_FIELD_TYPES = {
    "dropdown",
    "radio",
    "checkboxes",
    "multiselect",
    "conditional_dropdown_other",
    "conditional_multiselect_other",
}

BASE_INPUT_CLASS = "cigi-input"
BASE_SELECT_CLASS = "cigi-select"
BASE_GROUP_CLASS = "cigi-group"       # radios/checkbox groups
BASE_FILE_CLASS = "cigi-file-input"
BASE_DATE_CLASS = "cigi-date-input"  # date + datetime
ERROR_CLASS = "has-errors"


class LimitedChoiceMixin:
    sold_out_values = set()

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value and str(value) in self.sold_out_values:
            option["attrs"]["disabled"] = "disabled"
            option["attrs"]["aria-disabled"] = "true"
            option["label"] = f"{option['label']} (Sold out)"
        return option


class LimitedSelect(LimitedChoiceMixin, forms.Select):
    pass


class LimitedSelectMultiple(LimitedChoiceMixin, forms.SelectMultiple):
    pass


class LimitedRadioSelect(LimitedChoiceMixin, forms.RadioSelect):
    pass


class LimitedCheckboxSelectMultiple(LimitedChoiceMixin, forms.CheckboxSelectMultiple):
    pass


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
    'conditional_multiselect_other': forms.MultipleChoiceField,
    'radio': forms.ChoiceField,
    'mailchimp_optin': forms.ChoiceField,
    'date': forms.DateField,
    'datetime': forms.DateTimeField,
    'file': forms.FileField,
}


CONDITIONAL_OTHER_FIELD_TYPES = (
    "conditional_dropdown_other",
    "conditional_multiselect_other",
)


def is_non_answer_field_type(field_type: str) -> bool:
    return field_type in NON_ANSWER_FIELD_TYPES


def _selected_contains_trigger(selected, trigger_value: str) -> bool:
    if isinstance(selected, (list, tuple, set)):
        return trigger_value in {str(value).strip() for value in selected}
    return (selected or "").strip() == trigger_value


def parse_choice_limits(ff) -> dict[str, int]:
    limits = {}
    for line in (getattr(ff, "choice_limits", "") or "").splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        label, limit = [part.strip() for part in line.split("|", 1)]
        try:
            limits[label] = int(limit)
        except ValueError:
            continue
    return {label: limit for label, limit in limits.items() if limit > 0}


def _as_values(value) -> list[str]:
    if value in (None, "", False):
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value).strip()]


def _limited_fields(event, reg_type, *, is_guest_form=False):
    form_template = getattr(event, "registration_form_template", None)
    if not form_template:
        return []
    fields = []
    for ff in form_template.fields.all():
        if not _template_field_visible(ff, reg_type.slug, is_guest_form=is_guest_form):
            continue
        if ff.field_type in CHOICE_LIMIT_FIELD_TYPES and parse_choice_limits(ff):
            fields.append(ff)
    return fields


def _count_choice_usage(event, field_key: str, value: str, *, exclude_registrant=None) -> int:
    from .models import Registrant

    qs = Registrant.objects.filter(event=event).exclude(status=Registrant.Status.CANCELLED)
    if exclude_registrant is not None and getattr(exclude_registrant, "pk", None):
        qs = qs.exclude(pk=exclude_registrant.pk)

    key = f"f_{field_key}"
    count = 0
    for answers in qs.values_list("answers", flat=True):
        selected = (answers or {}).get(key)
        if value in _as_values(selected):
            count += 1
    return count


def _current_values(current_registrant, key: str) -> set[str]:
    answers = getattr(current_registrant, "answers", None)
    if not isinstance(answers, dict):
        return set()
    return set(_as_values(answers.get(key)))


def _sold_out_values(event, ff, current_registrant=None) -> set[str]:
    sold_out = set()
    key = f"f_{ff.field_key}"
    current = _current_values(current_registrant, key)
    for value, limit in parse_choice_limits(ff).items():
        if value in current:
            continue
        if _count_choice_usage(event, str(ff.field_key), value, exclude_registrant=current_registrant) >= limit:
            sold_out.add(value)
    return sold_out


def validate_choice_limits(event, reg_type, cleaned_data_list, *, current_registrant=None) -> dict[str, str]:
    errors = {}
    for ff in _limited_fields(event, reg_type):
        key = f"f_{ff.field_key}"
        selected_counts = {}
        for cleaned in cleaned_data_list:
            for value in _as_values((cleaned or {}).get(key)):
                selected_counts[value] = selected_counts.get(value, 0) + 1

        for value, selected_count in selected_counts.items():
            limit = parse_choice_limits(ff).get(value)
            if not limit:
                continue
            used = _count_choice_usage(event, str(ff.field_key), value, exclude_registrant=current_registrant)
            if used + selected_count > limit:
                errors[key] = f'"{value}" is sold out.'
                break
    return errors


def add_choice_limit_errors(form, errors):
    for key, message in errors.items():
        if key in form.fields:
            form.add_error(key, message)
        else:
            form.add_error(None, message)


def _template_field_visible(ff, current_slug: str, *, is_guest_form: bool) -> bool:
    if is_guest_form and getattr(ff, "exclude_from_guest_forms", False):
        return False

    vis_slugs = _split_slugs(ff.visible_type_slugs)
    return _match(ff.visible_rule, vis_slugs, current_slug)


def _answer_keys_for_template_field(ff) -> list[str]:
    base = f"f_{ff.field_key}"
    if ff.field_type == "conditional_text":
        return [f"{base}__enabled", f"{base}__details"]
    if ff.field_type in CONDITIONAL_OTHER_FIELD_TYPES:
        return [base, f"{base}__other"]
    return [base]


def strip_non_answer_data(event, data: dict) -> dict:
    """Remove display-only template rows from data before answer storage."""

    form_template = getattr(event, "registration_form_template", None)
    if not form_template:
        return data

    for ff in form_template.fields.all().only("field_key", "field_type"):
        if is_non_answer_field_type(getattr(ff, "field_type", "")):
            data.pop(f"f_{ff.field_key}", None)
    return data


def build_dynamic_form(
    event,
    reg_type,
    invite=None,
    *,
    require_email: bool = True,
    include_honeypot: bool = True,
    is_guest_form: bool = False,
    current_registrant=None,
):
    """
    Build a dynamic Form class from RegistrationFormField rules (no admin/panels tricks).
    """

    fields = []
    conditional_rules = []

    email_initial = invite.email if getattr(invite, "email", None) else None

    fields.append(("first_name", forms.CharField(label="First Name", required=True)))
    fields.append(("last_name", forms.CharField(label="Last Name", required=True)))
    email_field = forms.EmailField(label="Email", required=require_email, initial=email_initial)
    if email_initial:
        email_field.widget.attrs["readonly"] = "readonly"
    fields.append(("email", email_field))

    current_slug = reg_type.slug

    fields_qs = event.registration_form_template.fields.all()

    ordered_template_fields = list(fields_qs.order_by("sort_order"))

    for ff in ordered_template_fields:
        if not _template_field_visible(ff, current_slug, is_guest_form=is_guest_form):
            continue

        if is_non_answer_field_type(ff.field_type):
            continue

        req_slugs = _split_slugs(ff.required_type_slugs)
        is_required = bool(ff.required) or _match(ff.required_rule, req_slugs, current_slug)

        key = f"f_{ff.field_key}"
        FieldClass = WAGTAIL_FIELD_MAP.get(ff.field_type, forms.CharField)
        kwargs = {"label": ff.label, "help_text": ff.help_text, "required": is_required}

        if ff.field_type == "mailchimp_optin":
            field_obj = forms.ChoiceField(
                label=ff.label,
                help_text=ff.help_text,
                required=is_required,
                choices=[("Yes", "Yes"), ("No", "No")],
                widget=forms.RadioSelect(attrs={"class": BASE_GROUP_CLASS}),
            )
            fields.append((key, field_obj))
            continue

        if ff.field_type in ("dropdown", "radio", "checkboxes", "multiselect", "date", "datetime", "file"):
            choices = [(x.strip(), x.strip()) for x in ff.choices.splitlines() if x.strip()]
            if ff.field_type == "dropdown":
                choices = [("", "Select an option…")] + choices
            kwargs["choices"] = choices
            sold_out = _sold_out_values(event, ff, current_registrant)
            if ff.field_type == "dropdown":
                widget = LimitedSelect()
                widget.sold_out_values = sold_out
                kwargs["widget"] = widget
            if ff.field_type == "checkboxes":
                widget = LimitedCheckboxSelectMultiple()
                widget.sold_out_values = sold_out
                kwargs["widget"] = widget
            if ff.field_type == "radio":
                widget = LimitedRadioSelect()
                widget.sold_out_values = sold_out
                kwargs["widget"] = widget
            if ff.field_type == "multiselect":
                widget = LimitedSelectMultiple()
                widget.sold_out_values = sold_out
                kwargs["widget"] = widget
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
                    # Duplicate key for Django template-friendly access.
                    # Django templates can't access dict keys with hyphens via dot-notation.
                    "data_conditional_details_for": needs_key,
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
        if ff.field_type in CONDITIONAL_OTHER_FIELD_TYPES:
            base_key = f"f_{ff.field_key}"
            select_key = base_key
            other_key = f"{base_key}__other"
            is_multiselect = ff.field_type == "conditional_multiselect_other"

            choices = [(x.strip(), x.strip()) for x in ff.choices.splitlines() if x.strip()]
            if not is_multiselect:
                choices = [("", "Select an option…")] + choices

            other_value = (getattr(ff, "conditional_other_value", "") or "").strip() or "Other"
            other_label = (getattr(ff, "conditional_other_label", "") or "").strip() or "Please specify"
            other_help = getattr(ff, "conditional_other_help_text", "") or ""
            other_required = bool(getattr(ff, "conditional_other_required", True))

            select_field_class = forms.MultipleChoiceField if is_multiselect else forms.ChoiceField
            select_kwargs = {
                "label": ff.label,
                "required": is_required,
                "help_text": ff.help_text,
                "choices": choices,
            }
            if is_multiselect:
                widget = LimitedSelectMultiple()
            else:
                widget = LimitedSelect()
            widget.sold_out_values = _sold_out_values(event, ff, current_registrant)
            select_kwargs["widget"] = widget
            select_field = select_field_class(**select_kwargs)
            if is_multiselect:
                select_field.widget.attrs["class"] = f"{BASE_SELECT_CLASS} {BASE_SELECT_CLASS}--multiple".strip()
            else:
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
            # Duplicate key for Django template-friendly access.
            other_field.widget.attrs["data_conditional_details_for"] = select_key

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
    if include_honeypot:
        fields.append((
            HoneypotMixin.hp_field,
            forms.CharField(
                required=False,
                label="website",
                widget=forms.TextInput(attrs={"autocomplete": "off"}),
            ),
        ))

    attrs = dict(fields)
    attrs["__module__"] = __name__

    bases = (HoneypotMixin, forms.Form) if include_honeypot else (forms.Form,)
    DynamicForm = type("EventDynamicForm", bases, attrs)

    def _layout_items(self):
        items = []
        for ff in ordered_template_fields:
            if not _template_field_visible(ff, current_slug, is_guest_form=is_guest_form):
                continue

            if ff.field_type == "rich_text":
                content = getattr(ff, "rich_text", "")
                if content:
                    items.append({"kind": "rich_text", "content": content})
                continue

            for key in _answer_keys_for_template_field(ff):
                if key in self.fields:
                    items.append({"kind": "field", "field": self[key]})
        return items

    def _dynamic_clean(self):
        cleaned = super(DynamicForm, self).clean()

        for rule in conditional_rules:
            if rule.get("kind") == "select_other":
                selected = cleaned.get(rule["select_key"])
                other = (cleaned.get(rule["other_key"]) or "").strip()

                if _selected_contains_trigger(selected, rule["trigger_value"]):
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

        # If conditional detail/other fields are missing, those fields already
        # have errors, but add a top-level hint to reduce confusion.
        if self.errors and any(
            k.endswith("__details") or k.endswith("__other") for k in self.errors.keys()
        ):
            self.add_error(
                None,
                "Some questions need additional details. Please fill in the fields marked 'Please specify.'",
            )

        add_choice_limit_errors(
            self,
            validate_choice_limits(
                event,
                reg_type,
                [cleaned],
                current_registrant=current_registrant,
            ),
        )

        return cleaned

    DynamicForm.clean = _dynamic_clean
    DynamicForm.layout_items = _layout_items
    return DynamicForm

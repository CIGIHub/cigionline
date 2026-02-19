from django import template
from django import forms
from django.forms.widgets import ClearableFileInput, FileInput

register = template.Library()


@register.filter
def is_single_checkbox(bound_field):
    return isinstance(bound_field.field.widget, forms.CheckboxInput)


@register.filter
def is_choice_group(bound_field):
    return isinstance(bound_field.field.widget, (forms.RadioSelect, forms.CheckboxSelectMultiple))


@register.filter
def is_file(bound_field):
    return isinstance(bound_field.field.widget, (ClearableFileInput, FileInput))


@register.filter
def is_textarea(bound_field):
    return isinstance(bound_field.field.widget, forms.Textarea)


@register.filter
def is_conditional_toggle(field):
    w = getattr(field, "field", None).widget if getattr(field, "field", None) else None
    attrs = getattr(w, "attrs", {}) if w else {}
    return attrs.get("data-conditional-toggle") == "1"

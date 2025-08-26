from django.forms.models import BaseInlineFormSet


class RegistrationFormFieldInlineFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        # parent instance is the EventPage (possibly a Page subclass proxy)
        event = getattr(self, "instance", None)
        if hasattr(event, "specific"):
            event = event.specific

        qs = event.registration_types.all() if (event and event.pk) else event.registration_types.none()

        if "show_for_types" in form.fields:
            form.fields["show_for_types"].queryset = qs
        if "required_for_types" in form.fields:
            form.fields["required_for_types"].queryset = qs

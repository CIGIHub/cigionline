from django import forms
from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from wagtail.admin.forms import WagtailAdminPageForm


class EventPageAdminForm(WagtailAdminPageForm):
    registration_report_password = forms.CharField(
        label=_("Registration report password"),
        required=False,
        strip=False,
        widget=forms.PasswordInput(render_value=False),
        help_text=_(
            "Set or replace the password for the public registration report. "
            "Leave blank to keep the existing password."
        ),
    )
    clear_registration_report_password = forms.BooleanField(
        label=_("Clear registration report password"),
        required=False,
        help_text=_("Disable the public registration report for this event."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not getattr(self.instance, "registration_report_password_hash", ""):
            self.fields["registration_report_password"].help_text = _(
                "Set a password to enable the public registration report at "
                "this event's /registration-report/ URL."
            )

        RegistrationType = apps.get_model('events', 'RegistrationType')
        event = getattr(self.instance, 'specific', self.instance)

        # Build the base queryset: only this event's saved types
        if getattr(event, 'pk', None):
            base_qs = RegistrationType.objects.filter(event_id=event.pk).order_by('sort_order')
        else:
            base_qs = RegistrationType.objects.none()

        ff_formset = self.formsets.get('form_fields')
        if not ff_formset:
            return

        for form in ff_formset.forms:
            # Collect selected IDs from the instance (works with ParentalManyToManyField)
            selected_show = []
            selected_req = []
            if form.instance is not None:
                if hasattr(form.instance, 'show_for_types'):
                    selected_show = list(
                        form.instance.show_for_types.values_list('pk', flat=True)
                    )
                if hasattr(form.instance, 'required_for_types'):
                    selected_req = list(
                        form.instance.required_for_types.values_list('pk', flat=True)
                    )

            # Union in selected IDs to avoid "initial not in queryset" issues
            union_ids = set(selected_show) | set(selected_req)
            if union_ids:
                type_qs = base_qs | RegistrationType.objects.filter(pk__in=union_ids)
                type_qs = type_qs.distinct().order_by('sort_order', 'pk')
            else:
                type_qs = base_qs

            # Apply queryset + explicit initial (only when not POST-bound)
            for fname, sel in (
                ('show_for_types', selected_show),
                ('required_for_types', selected_req),
            ):
                if fname in form.fields:
                    f = form.fields[fname]
                    f.queryset = type_qs
                    f.label_from_instance = lambda rt: rt.name
                    if not form.is_bound:  # GET render after save / first load
                        f.initial = sel

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("registration_report_password")
        clear_password = cleaned_data.get("clear_registration_report_password")

        if password and clear_password:
            self.add_error(
                "clear_registration_report_password",
                _("Choose either a new report password or clear the existing one."),
            )

        return cleaned_data

    def save(self, commit=True):
        page = super().save(commit=False)

        if self.cleaned_data.get("clear_registration_report_password"):
            page.registration_report_password_hash = ""
        elif self.cleaned_data.get("registration_report_password"):
            page.registration_report_password_hash = make_password(
                self.cleaned_data["registration_report_password"]
            )

        if commit:
            page.save()
            self.save_m2m()

        return page

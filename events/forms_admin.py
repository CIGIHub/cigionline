# from django.apps import apps
# from wagtail.admin.forms import WagtailAdminModelForm


# class RegistrationFormFieldAdminForm(WagtailAdminModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         RegistrationType = apps.get_model('events', 'RegistrationType')

#         event = getattr(self.instance, "event", None)
#         print(event)
#         qs = RegistrationType.objects.none()
#         if event and event.pk:
#             qs = RegistrationType.objects.filter(event=event)

#         for fname in ("show_for_types", "required_for_types"):
#             if fname in self.fields:
#                 self.fields[fname].queryset = qs

#     def clean(self):
#         cleaned = super().clean()
#         event = getattr(self.instance, "event", None)
#         if not event:
#             return cleaned

#         for fname in ("show_for_types", "required_for_types"):
#             selected = cleaned.get(fname)
#             if selected:
#                 wrong = [t for t in selected if t.event_id != event.id]
#                 if wrong:
#                     self.add_error(fname, "Selected registration types must belong to this event.")
#         return cleaned

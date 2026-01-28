from django.apps import apps
from wagtail.admin.panels import InlinePanel
from wagtail.admin.panels.base import get_form_for_model

class RegistrationFormFieldPanel(InlinePanel):
    """InlinePanel that filters show_for_types / required_for_types to this event's types."""

    def get_form_options(self):
        opts = super().get_form_options()  # this returns {"formsets": {relation_name: formset_opts}}
        formset_opts = opts["formsets"][self.relation_name]

        # Get the base form Wagtail would use for the child model
        BaseChildForm = formset_opts.get("form")
        if BaseChildForm is None:
            BaseChildForm = get_form_for_model(self.db_field.related_model)

        RegistrationType = apps.get_model("events", "RegistrationType")

        # Build a new form class that filters the M2M fields using the parent page
        class FilteredChildForm(BaseChildForm):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                # Wagtail/modelcluster puts the parent on self.for_parent
                parent = getattr(self, "for_parent", None) or getattr(self.instance, "event", None)
                if hasattr(parent, "specific"):
                    parent = parent.specific

                if getattr(parent, "pk", None):
                    type_qs = RegistrationType.objects.filter(event_id=parent.pk).order_by("sort_order")
                else:
                    type_qs = RegistrationType.objects.none()

                for fname in ("show_for_types", "required_for_types"):
                    if fname in self.fields:
                        f = self.fields[fname]
                        f.queryset = type_qs
                        f.label_from_instance = lambda rt: rt.name  # nicer labels

        # Tell InlinePanel to use our filtered child form
        formset_opts["form"] = FilteredChildForm
        return opts

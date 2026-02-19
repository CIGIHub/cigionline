from wagtail.admin.forms import WagtailAdminPageForm
from django.apps import apps


class EventPageAdminForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

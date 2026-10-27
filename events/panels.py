from django.apps import apps
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from urllib.parse import urlencode
from wagtail.admin.panels import InlinePanel, Panel
from wagtail.admin.panels.base import get_form_for_model


class EmailCampaignPreviewPanel(Panel):
    class BoundPanel(Panel.BoundPanel):
        template_name = "events/admin/email_campaign_preview_panel.html"

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            context["preview_url"] = reverse("emailcampaign:preview_selected")
            context["initial_preview_url"] = self._get_initial_preview_url(
                context["preview_url"]
            )
            context.update(self._get_initial_preview_context())
            return context

        def _get_initial_preview_context(self):
            if not getattr(self.instance, "template_id", None):
                return {
                    "initial_preview_message": _("Select an email template to preview it."),
                }

            from .email_preview import build_email_campaign_preview

            preview = build_email_campaign_preview(
                request=self.request,
                template_obj=self.instance.template,
                event=getattr(self.instance, "event", None),
                include_statuses=getattr(self.instance, "include_statuses", ""),
                include_type_slugs=getattr(self.instance, "include_type_slugs", ""),
            )

            return {
                "initial_preview_subject": preview.subject,
                "initial_preview_email_body_html": preview.body_html,
                "initial_preview_event_title": preview.event_title,
                "initial_preview_registrant_label": preview.registrant_label,
                "initial_preview_using_real_registrant": preview.using_real_registrant,
            }

        def _get_initial_preview_url(self, preview_url):
            params = {}

            if getattr(self.instance, "template_id", None):
                params["template_id"] = self.instance.template_id

            if getattr(self.instance, "event_id", None):
                params["event_id"] = self.instance.event_id

            if getattr(self.instance, "include_statuses", ""):
                params["include_statuses"] = self.instance.include_statuses

            if getattr(self.instance, "include_type_slugs", ""):
                params["include_type_slugs"] = self.instance.include_type_slugs

            if not params:
                return preview_url

            return f"{preview_url}?{urlencode(params)}"


class EmailCampaignTestSendPanel(Panel):
    class BoundPanel(Panel.BoundPanel):
        template_name = "events/admin/email_campaign_test_send_panel.html"

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)

            if getattr(self.instance, "pk", None):
                context["send_test_url"] = reverse(
                    "emailcampaign:send_test",
                    args=[self.instance.pk],
                )
            else:
                context["send_test_url"] = ""

            return context


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

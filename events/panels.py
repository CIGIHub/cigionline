from wagtail.admin.panels import InlinePanel
from .forms_admin import RegistrationFormFieldInlineFormSet


class RegistrationFormFieldPanel(InlinePanel):
    def get_form_options(self):
        opts = super().get_form_options()
        formsets = opts.setdefault('formsets', {})
        # attach our custom formset to this relation
        current = formsets.get(self.relation_name, {})
        current['formset'] = RegistrationFormFieldInlineFormSet
        formsets[self.relation_name] = current
        return opts

import os

from django.views.generic import TemplateView


class RobotsView(TemplateView):
    content_type = 'text/plain'

    def get_template_names(self):
        if 'PYTHON_ENV' in os.environ and os.environ.get('PYTHON_ENV') == 'production':
            return 'robots/robots_production.txt'
        return 'robots/robots.txt'

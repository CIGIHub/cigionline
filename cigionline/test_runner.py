from django.conf import settings
from django.test.runner import DiscoverRunner


class FastTestRunner(DiscoverRunner):
    """Restore the Wagtail baseline normally created by migrations."""

    def setup_databases(self, **kwargs):
        old_config = super().setup_databases(**kwargs)

        from home.models import HomePage
        from wagtail.coreutils import get_supported_content_language_variant
        from wagtail.models import Locale, Page, Site

        Locale.objects.get_or_create(
            language_code=get_supported_content_language_variant(settings.LANGUAGE_CODE),
        )

        homepage = HomePage.objects.first()
        if homepage is None:
            root = Page.get_first_root_node() or Page.add_root(
                instance=Page(title='Root', slug='root'),
            )
            homepage = root.add_child(
                instance=HomePage(title='Home', slug='home'),
            )

        if not Site.objects.filter(is_default_site=True).update(root_page=homepage):
            Site.objects.create(
                hostname='localhost', root_page=homepage, is_default_site=True,
            )

        return old_config

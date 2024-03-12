from django.core.management.base import BaseCommand
from publications.models import PublicationSeriesListPage, PublicationListPage
from wagtail.models import Page
from wagtail.contrib.redirects.models import Redirect

class Command(BaseCommand):
    help = 'Move PublicationSeriesListPage and redirect its child pages'

    def handle(self, *args, **kwargs):
        # Step 1: Identify the pages
        try:
            publication_series_list_page = PublicationSeriesListPage.objects.first()
            new_parent = PublicationListPage.objects.get(url_path='/home/publications/')
        except (Exception):
            self.stdout.write(self.style.ERROR('Required pages not found.'))
            return

        old_url = publication_series_list_page.full_url
        old_path = publication_series_list_page.url_path
        child_pages = publication_series_list_page.get_children()

        # Step 2: Move the PublicationSeriesListPage
        publication_series_list_page.move(new_parent, pos='last-child')
        new_url = publication_series_list_page.full_url

        # Create a redirect for the PublicationSeriesListPage itself (if needed)
        if old_url != new_url:
            Redirect.objects.create(
                old_path=old_path,
                site=publication_series_list_page.get_site(),
                redirect_page=publication_series_list_page,
                is_permanent=True
            )

        # Step 3: Redirect all child pages
        for child_page in child_pages:
            old_child_url = child_page.full_url  # URL before the move
            child_page.specific.save_revision()  # Save a new revision to update the url_path
            new_child_url = child_page.full_url  # URL after the move

            # Create a redirect from the old URL to the new URL
            if old_child_url != new_child_url:
                Redirect.objects.create(
                    old_path=child_page.url_path,
                    site=child_page.get_site(),
                    redirect_page=child_page,
                    is_permanent=True
                )

                self.stdout.write(self.style.SUCCESS(f'Redirected "{child_page.title}" from {old_child_url} to {new_child_url}'))

        self.stdout.write(self.style.SUCCESS('Completed moving PublicationSeriesListPage and redirecting child pages.'))

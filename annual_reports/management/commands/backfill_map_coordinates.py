from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db.models import Q
from geopy.exc import GeopyError
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

from annual_reports.models import MapStory, _geocode_cache_key


class Command(BaseCommand):
    help = 'Backfill missing MapStory coordinates from the cache or Nominatim.'

    def handle(self, *args, **options):
        geocode = RateLimiter(
            Nominatim(user_agent='cigi-ar-map', timeout=10).geocode,
            min_delay_seconds=1.1,
            max_retries=1,
            swallow_exceptions=False,
        )
        stories = MapStory.objects.filter(
            Q(latitude__isnull=True) | Q(longitude__isnull=True)
        )
        resolved = {}
        updated = 0
        failed = set()

        for story in stories.iterator():
            location = story.location.strip()

            if not location:
                failed.add('(empty location)')
                continue

            key = location.casefold()

            if key not in resolved:
                coordinates = cache.get(_geocode_cache_key('location', location))

                if not coordinates:
                    try:
                        result = geocode(location)
                    except GeopyError as exc:
                        self.stderr.write(f'Geocoding failed for {location}: {exc}')
                        result = None

                    if result:
                        coordinates = {
                            'latitude': result.latitude,
                            'longitude': result.longitude,
                        }

                resolved[key] = coordinates

            coordinates = resolved[key]

            if not coordinates:
                failed.add(location)
                continue

            MapStory.objects.filter(pk=story.pk).update(
                latitude=coordinates['latitude'],
                longitude=coordinates['longitude'],
            )
            updated += 1

        self.stdout.write(self.style.SUCCESS(f'Updated {updated} MapStory snippets.'))

        if failed:
            self.stdout.write(
                self.style.WARNING(f'{len(failed)} locations could not be resolved:')
            )
            for location in sorted(failed):
                self.stdout.write(f'  - {location}')

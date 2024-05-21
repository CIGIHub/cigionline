from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Clear the cache for all_experts'

    def handle(self, *args, **options):
        cache.delete_pattern("*all_experts*")
        self.stdout.write(self.style.SUCCESS('Cache cleared for all_experts'))

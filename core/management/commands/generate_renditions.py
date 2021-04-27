import base64

import requests

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db.models import Q

from wagtail.images import get_image_model


RENDITIONS = [
    'fill-1600x900',
    'original',
    'width-300',
    'fill-100x100',
    'fill-377x246',
    'width-1760',
    'width-640',
    'width-700',
    'fill-600x238',
    'fill-672x895',
    'width-100',
    'width-600',
    # These rendition types are used in 2 or fewer templates
    # skipped to speed up the process
    # 'fill-1440x990',
    # 'width-1280',
    # 'width-1440',
    # 'width-500',
    # 'fill-140x140',
    # 'fill-150x150',
    # 'fill-200x200',
    # 'fill-520x390',
    # 'fill-600x600',
    # 'fill-600x900',
    # 'max-450x200',
    # 'width-1024',
    # 'width-1920',
    # 'width-200',
    # 'width-768',
]


class Command(BaseCommand):

    def handle(self, **options):

        Image = get_image_model()

        images = Image.objects.all()

        print(f"Generating renditions for {images.count()} images...")

        for image in images:
            
            for rendition in RENDITIONS:
                try:
                    image.get_rendition(rendition)
                except:
                    pass
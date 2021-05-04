from django.db import models

from wagtail.images.models import Image, AbstractImage, AbstractRendition


class CigionlineImage(AbstractImage):
    caption = models.CharField(max_length=1024, blank=True)

    admin_form_fields = Image.admin_form_fields + (
        'caption',
    )


class CigionlineRendition(AbstractRendition):
    image = models.ForeignKey(CigionlineImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )

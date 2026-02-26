from django.core.files.base import ContentFile
from django.db import models

from wagtail.images.models import Image, AbstractImage, AbstractRendition


class CigionlineImage(AbstractImage):
    caption = models.CharField(max_length=1024, blank=True)

    admin_form_fields = Image.admin_form_fields + (
        'caption',
    )

    def generate_rendition_file(self, filter, *, source=None):
        """
        Override to buffer the generated SpooledTemporaryFile into an
        in-memory ContentFile before returning.

        Django 5.2 introduced ImageFieldFile._set_instance_attribute which
        triggers update_dimension_fields(force=True) immediately after S3
        uploads the file. S3 (django-storages) closes the underlying
        SpooledTemporaryFile during upload, causing Django to fail when it
        tries to re-read the file for dimensions. A ContentFile (BytesIO)
        is not closed by S3, so dimensions can still be read afterward.
        """
        generated_file = super().generate_rendition_file(filter, source=source)
        generated_file.seek(0)
        return ContentFile(generated_file.read(), name=generated_file.name)


class CigionlineRendition(AbstractRendition):
    image = models.ForeignKey(CigionlineImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )

from wagtail.documents.models import Document
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from django.db import models


class DocumentUpload(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='+'
    )
    email = models.EmailField()

    panels = [
        FieldPanel('document'),
        FieldPanel('email'),
    ]

    def __str__(self):
        return f"{self.document.title} - {self.email}"


register_snippet(DocumentUpload)

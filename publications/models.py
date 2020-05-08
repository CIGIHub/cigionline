from core.models import BasicPageAbstract, ShareablePageAbstract
from django.db import models
from modelcluster.fields import ParentalManyToManyField


class PublicationListPage(BasicPageAbstract):
    """Publication list page"""

    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['publications.PublicationPage']
    templates = 'publications/publication_list_page.html'

    class Meta:
        verbose_name = 'Publication List Page'


class PublicationPage(BasicPageAbstract, ShareablePageAbstract):
    """View publication page"""

    image_cover = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Cover image',
        help_text='An image of the cover of the publication.',
    )
    topics = ParentalManyToManyField('research.TopicPage', blank=True)

    parent_page_types = ['publications.PublicationListPage']
    subpage_types = []
    templates = 'publications.publication_page.html'

    class Meta:
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'

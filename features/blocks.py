from wagtail.blocks import StructBlock, PageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from promotions.models import PromotionBlock


class FeaturedPageBlock(StructBlock):
    page_types = [
        'publications.PublicationPage',
        'articles.ArticlePage',
        'articles.ArticleSeriesPage',
        'multimedia.MultimediaPage',
        'multimedia.MultimediaSeriesPage',
        'events.EventPage',
        'research.ProjectPage',
        'annual_reports.AnnualReportPage',
        'publications.T7PublicationPage',
        'annual_reports.StrategicPlanSPAPage',
    ]
    page = PageChooserBlock(page_type=page_types)

    class Meta:
        icon = 'pick'


class FeaturedPublicationBlock(StructBlock):
    page_types = [
        'publications.PublicationPage',
    ]
    page = PageChooserBlock(page_type=page_types)

    class Meta:
        icon = 'pick'


class FeaturedExpertBlock(StructBlock):
    page_types = [
        'people.PersonPage',
    ]
    page = PageChooserBlock(page_type=page_types)

    class Meta:
        icon = 'person'


class FeaturedHighlightBlock(StructBlock):
    page_types = [
        'publications.PublicationPage',
        'articles.ArticleSeriesPage',
    ]
    page = PageChooserBlock(page_type=page_types)

    class Meta:
        icon = 'pick'


class FeaturedMultimediaBlock(StructBlock):
    page_types = [
        'multimedia.MultimediaPage',
    ]
    page = PageChooserBlock(page_type=page_types)

    class Meta:
        icon = 'play'


class FeaturedEventBlock(StructBlock):
    page_types = [
        'events.EventPage',
    ]
    page = PageChooserBlock(page_type=page_types)

    class Meta:
        icon = 'calendar'


class FeaturedPromotionBlock(StructBlock):
    block = SnippetChooserBlock(PromotionBlock)

    class Meta:
        icon = 'pick'

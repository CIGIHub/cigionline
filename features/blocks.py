from wagtail.core.blocks import StructBlock, PageChooserBlock


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
    page_types = [
        'promotions.PromotionBlock',
    ]
    page = PageChooserBlock(page_type=page_types)

    class Meta:
        icon = 'pick'

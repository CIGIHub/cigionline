from django import template

from core.cards import (
    _card_excerpt,
    card_data,
    display_title as _display_title,
    expert_data,
    social_icon,
    topic_pills as _topic_pills,
    type_of_content_data,
)

register = template.Library()


@register.filter
def display_title(page):
    """``{{ item|display_title }}`` — feature_title over page title on listing
    rows that don't go through ``{% card %}`` (router item templates)."""
    return _display_title(page)


@register.filter
def card_excerpt(page):
    """``{{ item|card_excerpt }}`` — the card excerpt fallback chain
    (feature_subtitle → subtitle → short_description, stripped) for router
    item templates. ``search_result_description`` is unpopulated site-wide,
    so rows must not read it directly."""
    return _card_excerpt(page)


@register.filter
def topic_pills(topics, page=None):
    """``{{ item.topics.all|topic_pills:item }}`` — pills with the site-wide
    topic→theme accents for router item templates that render pills directly
    (card/_pills.html shape: [{'label', 'accent', 'url'}]). Pass the item so the
    pills link into its content type's router (Evan, 2026-09-10)."""
    return _topic_pills(topics, page=page)


@register.inclusion_tag('includes/card.html', takes_context=True)
def card(context, page, variant='media-vertical', pills=None, cta_label='Read More',
         cta_scheme='on-light', show_date=None, show_author=False,
         show_excerpt=False, tall_media=False):
    """Render a shared content card for a page.

    Usage: ``{% card page variant="article-list-row" %}``. Data comes from
    core.cards.card_data; the template renders the given variant. Pass ``pills``
    (a list of ``{'label', 'accent'}``) to override the page's own project pills
    — e.g. a module that locks cards to the program/context they're shown under.
    ``cta_label`` sets the media-variant CTA text (e.g. "Learn More").

    ``takes_context`` so the page link resolves relative to the current request's
    site (``get_url(request)``) rather than the Site's absolute root URL.
    """
    data = card_data(page, variant=variant, pills=pills, cta_label=cta_label,
                     cta_scheme=cta_scheme,
                     show_date=show_date, show_author=show_author,
                     request=context.get('request'))
    # media-stacked renders its excerpt only where the design asks for it (the
    # bento's mobile rail, Figma 1363-124701) — the desktop left column omits it.
    data['show_excerpt'] = show_excerpt
    # Duo-bento features flex their image to fill the row height (BugHerd #31),
    # so they fetch a taller rendition than the 16:9 default.
    data['tall_media'] = tall_media
    return data


@register.inclusion_tag('includes/expert_card.html', takes_context=True)
def expert_card(context, person, slots=None, show_title=True, show_bio=False,
                show_expertise=False, show_latest_activity=False,
                show_read_bio=False):
    """Render a shared expert/person card for a PersonPage.

    The card is one base archetype (avatar + name always on) plus four
    independently toggleable slots — title/role, bio, expertise tags, latest
    activity. Each renders only when its toggle is on AND the data is present.
    Data comes from core.cards.expert_data (the full superset; visibility is
    decided here).

    Consuming modules drive the toggles. Either pass the ``show_*`` flags
    directly, or pass ``slots`` — a dict / StructValue from an
    ``ExpertCardSlotsBlock`` (keys match the ``show_*`` args), e.g.
    ``{% expert_card person slots=self.card_slots %}``.
    """
    if slots is not None:
        show_title = slots.get('show_title', show_title)
        show_bio = slots.get('show_bio', show_bio)
        show_expertise = slots.get('show_expertise', show_expertise)
        show_latest_activity = slots.get('show_latest_activity', show_latest_activity)
        show_read_bio = slots.get('show_read_bio', show_read_bio)
    data = expert_data(person, request=context.get('request'))
    data['show_title'] = show_title
    data['show_bio'] = show_bio
    data['show_expertise'] = show_expertise
    data['show_latest_activity'] = show_latest_activity
    data['show_read_bio'] = show_read_bio
    return data


@register.inclusion_tag('includes/type_of_content.html')
def type_of_content(page):
    """Render the type-of-content molecule (icon + uppercase label) for a page.
    Usage: ``{% type_of_content page %}``."""
    return type_of_content_data(page)


@register.inclusion_tag('includes/share_buttons.html')
def share_buttons(links, heading='Follow'):
    """Render the share / follow buttons molecule — a label + circular social icon
    links. ``links`` is an iterable of ``{'platform', 'url'}`` (optional 'label');
    each platform maps to a Font Awesome brand glyph. Links without a url are
    skipped; a link whose platform has no known glyph renders as a plain text
    link (so an odd subscribe platform still shows). Used across
    article/publication/podcast heroes.
    """
    resolved = []
    for link in links or []:
        url = link.get('url')
        if not url:
            continue
        resolved.append({
            'url': url,
            'icon': social_icon(link.get('platform', '')),
            'label': link.get('label') or link.get('platform', '').title(),
        })
    return {'heading': heading, 'links': resolved}


@register.inclusion_tag('includes/resource_carousel.html', takes_context=True)
def recommended_carousel(context, page, heading='Explore Recommended', count=9, surface='light'):
    """Render the shared resource-carousel rail populated from a content page's
    recommendations — the single-template "Explore Recommended" section. Data is ``ContentPage.recommended_content``: the editor-curated
    Recommended panel picks first, topped up automatically with the most recent
    live content sharing the page's topics. In page preview the uncached
    ``recommended_content_preview`` variant is used so curation edits show.
    """
    request = context.get('request')
    if request is not None and getattr(request, 'is_preview', False) \
            and page.recommended_content_preview:
        pages = page.recommended_content_preview
    else:
        pages = page.recommended_content
    pages = list(pages[:count])
    return {
        'request': request,
        'heading': heading,
        'surface': surface,
        # Page-level accent scheme (e.g. DPH green) carries into the rail.
        'main_accent_scheme': context.get('main_accent_scheme'),
        'feature': pages[0] if pages else None,
        'compact_cards': pages[1:],  # one card per slide (BugHerd #68)
        # The rail template reads `loop` (authorable on ResourceCarouselBlock);
        # these tag-driven rails have no block, so keep looping on.
        'loop': True,
    }


@register.inclusion_tag('includes/supporting_materials.html')
def supporting_materials(page, heading='Supporting Materials'):
    """Render the shared supporting-materials carousel from a page's attached
    documents — nothing renders when the page has none.
    Sources: ``related_files`` (articles / events / basic pages) and any ePub
    downloads. A publication's own PDFs are NOT here — every edition renders as
    a hero button (Tim, BugHerd #474: the French edition belongs beside the
    English one, not inside this drawer).
    """
    items = []

    def add(doc, label):
        if doc:
            items.append({
                'title': doc.title,
                'content_type': (doc.file_extension or 'file').upper(),
                'url': doc.url,
                'download': True,
                'button_label': label,
            })

    for block in (getattr(page, 'related_files', None) or []):
        add(block.value, 'Download')
    for block in (getattr(page, 'book_epub_downloads', None) or []):
        add(block.value.get('file'), block.value.get('button_text') or 'Download Book')

    return {'heading': heading if items else None, 'items': items, 'loop': False}


@register.filter
def stream_has(body, block_type):
    """True when a StreamField value contains a block of the given type."""
    return any(b.block_type == block_type for b in body)


@register.filter
def midpoint(count):
    """1-based index of the middle item — where the reading body inserts the
    fixed Subscribe CTA (mid-body)."""
    return (int(count) + 1) // 2


# DS section modules that can sit in a page body stream. The reading shell
# wraps these in `.ds-prose__module` so the prose element rules (p/a/h*/lists
# — meant for the reading content and the legacy block output) don't restyle
# module internals (underlined card titles, serif 16px module headings —
# staging module pass 2026-07-14). Reading-level blocks (paragraph, quotes,
# charts, plain accordion, …) stay unwrapped: prose styling IS their styling.
# Keep in sync with the module entries on core.models.BasicPageAbstract.
DS_MODULE_TYPES = frozenset({
    'accordion_module', 'alt_hero', 'banner', 'composable_tabs', 'cta_image',
    'events_carousel', 'experts_carousel', 'experts_grid', 'faceted_listing',
    'form', 'gallery_text', 'horizontal_tabs', 'image_text', 'jobs_list',
    'news_carousel', 'news_grid', 'newsletter_subscription', 'primary_hero',
    'program_grid', 'program_spotlight', 'programs_carousel', 'resource_bento',
    'resource_carousel', 'split_hero', 'stats', 'supporting_materials',
    'text_card_grid', 'text_columns', 'trending_issues', 'video_carousel',
    'video_text',
})


@register.filter
def is_ds_module(block):
    """True when a stream child is a DS section module (vs reading content)."""
    return getattr(block, 'block_type', None) in DS_MODULE_TYPES


# Page-level aside block types the body loops never render inline (they feed
# dedicated sections/tables elsewhere) — same exclusions as reading_body.html.
_BODY_ASIDE_TYPES = frozenset({'additional_disclaimer', 'additional_file'})

# Hero modules an author can open a body with — a page whose body starts with
# one supplies its own hero, so the page-level hero must not double up.
_HERO_MODULE_TYPES = frozenset({'split_hero', 'primary_hero', 'alt_hero'})


@register.filter
def starts_with_hero(body):
    """True when the body's first block is an authored hero module."""
    for block in body:
        return getattr(block, 'block_type', None) in _HERO_MODULE_TYPES
    return False


@register.filter
def body_sections(body):
    """Group a body StreamField into alternating sections for a DS page shell:
    DS modules render full-bleed on their own, contiguous non-module (prose)
    blocks share one reading measure. Returns
    ``[{'kind': 'module', 'block': b} | {'kind': 'prose', 'blocks': [...]}]``."""
    sections = []
    for block in body:
        if getattr(block, 'block_type', None) in _BODY_ASIDE_TYPES:
            continue
        if is_ds_module(block):
            sections.append({'kind': 'module', 'block': block})
        elif sections and sections[-1]['kind'] == 'prose':
            sections[-1]['blocks'].append(block)
        else:
            sections.append({'kind': 'prose', 'blocks': [block]})
    return sections


@register.simple_tag
def button_scheme(scheme, surface=''):
    """Resolve a ButtonBlock's scheme class. An authored scheme wins; 'auto'
    (the default) maps from the surrounding module's surface — templates pass
    `button_surface` (banner/stats: their surface picker; cta_image: 'red').
    White-text colour surfaces take on-dark (incl. the DPH charcoal + forest
    green, 1595:95086)."""
    if scheme and scheme != 'auto':
        return scheme
    if surface == 'red':
        return 'on-red'
    if surface in ('dark', 'charcoal', 'green', 'teal', 'blue', 'olive', 'mauve'):
        return 'on-dark'
    return 'on-light'


@register.inclusion_tag('streams/events_carousel_block.html', takes_context=True)
def more_events_carousel(context, page, heading='More Events', count=9):
    """Events-carousel rail on the event single (Event Template —
    the design's related section for events; reuses the existing module, per
    Evan the frame's layout variant is not a standalone module). Most recent
    live events, excluding the page itself."""
    from events.models import EventPage

    events = list(
        EventPage.objects.live().public()
        .filter(publishing_date__isnull=False)
        .exclude(id=page.id)
        .order_by('-publishing_date')[:count]
    )
    return {
        'request': context.get('request'),
        'self': {'heading': heading, 'show_pagination': True,
                 'surface': 'light', 'accent': 'red'},
        'events': events,
        'cta_url': None,
        'cta_scheme': 'on-light',
    }


@register.inclusion_tag('includes/resource_carousel.html', takes_context=True)
def continue_listening(context, page, heading=None, count=9, surface='light'):
    """Same-series episode rail on the podcast single (the Podcast Carousel
    section). Renders nothing without a series.

    The default heading follows the episode's medium: a video single reads
    "Continue Watching", an audio single "Continue Listening" (Tim, BugHerd
    #511 — a video keynote carried the podcast heading)."""
    from multimedia.models import MultimediaPage

    if heading is None:
        heading = ('Continue Watching' if getattr(page, 'multimedia_type', '') == 'video'
                   else 'Continue Listening')
    series = getattr(page, 'multimedia_series', None)
    if series is None:
        return {'request': context.get('request'), 'heading': None,
                'surface': surface, 'feature': None, 'compact_cards': [], 'loop': True}
    pages = list(
        MultimediaPage.objects.live().public()
        .filter(multimedia_series=series, publishing_date__isnull=False)
        .exclude(id=page.id)
        .order_by('-publishing_date')[:count]
    )
    return {
        'request': context.get('request'),
        'heading': heading if pages else None,
        'surface': surface,
        'feature': pages[0] if pages else None,
        'compact_cards': pages[1:],  # one card per slide (BugHerd #68)
        'loop': True,  # tag-driven rail: no block field to author
    }

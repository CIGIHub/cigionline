"""Card data layer.

A polymorphic presenter that normalises any page into the context a `{% card %}`
renders, plus the standalone `project_pills` accessor reused by every dynamic-module
consumer of "a logical card representing a page". Page-type dispatch lives here so
templates stay dumb. No model imports needed at module load (relations are reached
via attributes), so this is safe to import anywhere.
"""

import html

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.html import strip_tags

# Variants that render a feature image + serif excerpt. Listed here so the
# presenter only touches the image/excerpt fields (and their FK query) for cards
# that actually show them — the list variants (article-list-row) stay query-light.
MEDIA_VARIANTS = {'media-vertical', 'media-compact', 'media-stacked', 'event'}


def _project_accent(project):
    # program -> theme accent; ThemeProgram is the only theme<->program edge.
    # Unmapped falls back to neutral grey, not brand red — red implied a theme
    # that doesn't exist (Kay, BugHerd #326).
    membership = project.theme_memberships.select_related('theme').first()
    if membership and membership.theme:
        return membership.theme.accent_colour
    return 'grey'


# Social/podcast platform -> Font Awesome brand glyph. Central so every share /
# follow / podcast-platform row resolves the same icon for a given platform.
SOCIAL_ICONS = {
    'x': 'fa-x-twitter',
    'twitter': 'fa-x-twitter',
    'linkedin': 'fa-linkedin-in',
    'instagram': 'fa-instagram',
    'facebook': 'fa-facebook-f',
    'youtube': 'fa-youtube',
    'spotify': 'fa-spotify',
    'apple': 'fa-apple',
    'apple-podcasts': 'fa-apple',
    'apple podcasts': 'fa-apple',
    'apple music': 'fa-apple',
    'youtube music': 'fa-youtube',
    'amazon music': 'fa-amazon',
    'rss': 'fa-rss',
}


def social_icon(platform):
    """The Font Awesome brand glyph for a social/podcast platform (e.g. 'spotify'
    -> 'fa-spotify'). '' for unknown platforms so callers can skip them."""
    return SOCIAL_ICONS.get((platform or '').lower(), '')


def topic_accent(topic):
    """A topic's site-wide accent colour = its ``program_theme``'s theme accent
    (neutral grey when unmapped — red read as a theme colour, Kay, BugHerd #326).
    The single source of topic->accent everywhere a
    topic pill/dot renders, so a given topic shows one consistent colour site-wide.
    The topic counterpart to ``_project_accent`` (projects map via ThemeProgram;
    topics map via ``TopicPage.program_theme``)."""
    theme = getattr(topic, 'program_theme', None)
    return theme.accent_colour if theme else 'grey'


def _page_path(page):
    """Relative path for a pill link. ``page.url`` has no request here and falls
    back to the Site's absolute root_url (the prod host) off-prod; the path part
    of ``get_url_parts()`` is host-independent."""
    parts = page.get_url_parts() if hasattr(page, 'get_url_parts') else None
    return parts[2] if parts else getattr(page, 'url', '')


def topic_pills(topics, page=None):
    """Pills for an iterable of ``TopicPage`` as ``[{'label', 'accent', 'url'}]``,
    accent via the site-wide topic->theme mapping. ``select_related('program_theme')``
    upstream to keep it query-light.

    Each pill links to the topic's theme page with the topic pre-selected in
    that page's resource listing (``core.router_links``, sync 2026-09-21). A
    topic with no theme, or a theme page with no listing yet → ``url`` is None
    and the pill renders plain. ``page`` is accepted for the existing callers
    and unused: the link no longer depends on the card's content type."""
    from core.router_links import topic_theme_url
    return [{'label': topic.title, 'accent': topic_accent(topic),
             'url': topic_theme_url(topic)} for topic in topics]


def project_pills(page):
    """A page's project/program pills as ``[{'label', 'accent', 'url'}]``.

    Standalone — callable by any module, not just the card. Cards no longer
    use it (card pills are topics only, see ``page_pills``); the expert hero's
    programs row does, and so does the content hero's pill row on a page with
    no topics (BugHerd #514). The display cap (2-3) is applied in the template, not
    here, so callers can see the full set.
    """
    projects = getattr(page, 'projects', None)
    if projects is None:
        return []
    # Current-IA programs only (theme-mapped): a legacy program tag drew a
    # red-fallback pill with a retired initiative's name, which read as noise
    # (Tim, BugHerd #326).
    pills = []
    for project in projects.all():
        membership = project.theme_memberships.select_related('theme').first()
        if membership and membership.theme:
            # Program pills link to the program page (Evan, 2026-09-10).
            pills.append({'label': project.title,
                          'accent': membership.theme.accent_colour,
                          'url': _page_path(project)})
    return pills


# The Digital Policy Hub is a CIGI initiative with its own brand, not a program
# under a theme, so it never reaches project_pills. A person belongs to it via
# their person type — the hub's own tags (core.faceted_listing.PERSON_TYPE_IDS).
DPH_PERSON_TYPE_IDS = (17, 18)  # Digital Policy Hub Fellow, DPH Speaker
DPH_PILL = {'label': 'Digital Policy Hub', 'accent': 'green', 'url': None}


def hub_pills(person):
    """A plain (unlinked) Digital Policy Hub pill for a person who carries a
    DPH person type, else nothing. Requested for the expert hero's program row
    so shared experts read as hub people too (Tim, BugHerd #372; Tia: not
    clickable)."""
    types = getattr(person, 'person_types', None)
    if types is None:
        return []
    if types.filter(id__in=DPH_PERSON_TYPE_IDS).exists():
        return [dict(DPH_PILL)]
    return []


def page_pills(page):
    """The default pill set for a page's card: its topics, always (Evan,
    2026-09-22). Card pills never name a program.

    History: events pilled on topics from the start (BugHerd #8); other cards
    pilled on the current-IA program first (BugHerd #326) and fell back to
    topics only when the page had none (BugHerd #228). The program-first rule
    put "Africa's Digital Transformation" on the Investment Treaties card and
    CIGI read it as a mis-tagged topic — the two pill kinds look identical.
    Programs stay reachable through the breadcrumb and the hero eyebrow;
    ``project_pills`` remains for the expert hero's programs row and the
    content hero of a topic-less page (BugHerd #514).

    A page with no topics draws no pill row — topic tagging is the content
    lever, as is mapping each topic to its theme for the pill colour and link.
    """
    topics = getattr(page, 'topics', None)
    if topics is None:
        return []
    return topic_pills(topics.select_related('program_theme'), page=page)


def _twitter_url(handle):
    """A profile URL from the authored `twitter_username` field, which holds
    handles ('@name' or 'name') — rendered raw it becomes a broken relative
    href. Full URLs pass through."""
    handle = (handle or '').strip()
    if not handle:
        return ''
    if handle.startswith('http://') or handle.startswith('https://'):
        return handle
    return f'https://x.com/{handle.lstrip("@")}'


def expert_data(person, request=None):
    """The shared expert superset for a ``PersonPage``.

    Returns the six person-card slots — name · role · avatar · bio ·
    expertise-tags · latest-activity — plus ``programs`` and ``share_links``,
    which only the Expert Bio Hero renders. One fetch so the hero and every
    expert-consuming card draw from a single source; slot *visibility* is a
    per-block author concern, so this always returns the full set and the
    template/module decides what to show.

    Expertise tags are read from the materialized ``derived_topics`` (kept current
    by the ``update_expert_topics`` command) — never computed on the fly. Programs
    reuse the project-pill accent rule. For lists, prefetch ``derived_topics`` /
    ``projects`` and ``content_pages_as_author__content_page`` in the module.
    """
    person = person.specific
    name = person.title or ' '.join(
        part for part in (person.first_name, person.last_name) if part
    ).strip()

    # Use the prefetched `_live_authored` (set by the experts list queryset) to
    # avoid a per-person query in lists; fall back to a direct query (e.g. the
    # single Expert hero, where no prefetch is set up).
    prefetched = getattr(person, '_live_authored', None)
    if prefetched is not None:
        latest = prefetched[0] if prefetched else None
    else:
        latest = (person.content_pages_as_author
                  .filter(content_page__live=True)
                  .select_related('content_page')
                  .order_by('-content_page__publishing_date')
                  .first())
    latest_activity = None
    if latest and latest.content_page:
        content = latest.content_page
        latest_activity = {
            'title': content.title,
            'url': content.get_url(request=request),
            'date': getattr(content, 'publishing_date', None),
        }

    return {
        'url': person.get_url(request=request),
        'name': name,
        'role': person.position,
        'avatar': person.image_square,
        'bio': person.short_bio,
        'expertise_tags': topic_pills(
            person.derived_topics.select_related('program_theme')
        ),
        'latest_activity': latest_activity,
        # Hero-only slots (kept here so hero + cards share one fetch):
        'programs': project_pills(person) + hub_pills(person),
        'share_links': {
            'linkedin': person.linkedin_url or '',
            'twitter': _twitter_url(person.twitter_username),
        },
    }


def _card_image(page):
    """Best feature image for a card: image_feature, falling back to image_hero."""
    return getattr(page, 'image_feature', None) or getattr(page, 'image_hero', None)


def _card_authors(page, request=None):
    """A card byline: the page's authors as ``[{'name', 'url'}]``, each URL the
    author's bio (PersonPage) page. Reads the ``ContentPageAuthor`` through-rows
    (``author`` = PersonPage); empty for pages without authors. Consuming modules
    should ``prefetch_related('authors__author')`` to keep this query-light."""
    rows = getattr(page, 'authors', None)
    if rows is None:
        return []
    authors = []
    for row in rows.all():
        person = getattr(row, 'author', None)
        if person:
            authors.append({'name': person.title, 'url': person.get_url(request=request)})
    return authors


def display_title(page):
    """Listing title for a card/row: the promotional ``feature_title`` wins over
    the page title where authored (legacy features/listing-surface behaviour;
    211 live pages differ). Companion to ``_card_excerpt``'s feature_subtitle
    preference. Singles/heroes keep ``page.title``."""
    return getattr(page, 'feature_title', '') or page.title


def _card_excerpt(page):
    """Short serif intro for media cards. The plain ``feature_subtitle`` wins;
    otherwise the rich ``subtitle`` / ``short_description`` are stripped to text.

    Publications reverse those two. PublicationPage has no numbering field, so
    editors type the series number into ``subtitle`` ("Policy Brief No. 236")
    and the prose lives in ``short_description`` — reading ``subtitle`` first
    put a label where the card design wants a description (BugHerd #138). On
    staging 883 of 1695 live publications carry a label-like subtitle, and none
    has a subtitle without a short_description, so the swap never loses text.
    """
    feature_subtitle = getattr(page, 'feature_subtitle', None)
    if feature_subtitle:
        return html.unescape(feature_subtitle).strip()
    fields = ('subtitle', 'short_description')
    if page.__class__.__name__ == 'PublicationPage':
        fields = ('short_description', 'subtitle')
    for field in fields:
        value = getattr(page, field, None)
        if value:
            # Imported values can hold literal entities ("Jury&#x27;s");
            # without unescaping, autoescape doubles them into "&amp;#x27;"
            # on cards and heroes (BugHerd #406). strip_tags leaves entities
            # alone, so decode to plain text — the template re-escapes safely.
            return html.unescape(strip_tags(value)).strip()
    return ''


def _card_type_label(page):
    """Type-of-content label for a card (e.g. "Opinion", "Policy Brief"). Uses the
    page's ``contentsubtype`` property, guarding the FK lookups it does internally."""
    try:
        label = page.contentsubtype or ''
    except (AttributeError, ObjectDoesNotExist):
        return ''
    # Programs report "Activity" internally, which reads as a content type the
    # site doesn't have. Juode (BugHerd #201): "if there's one anyway, can it
    # say Topic".
    return 'Topic' if label == 'Activity' else label


def _card_type_icon(page):
    """Font Awesome (light) glyph for a page's content type.

    Reconciles the redesign icon legend with the legacy feature icons. The one
    new split: CIGI-in-the-News / News Releases get the megaphone (`fa-bullhorn`),
    distinct from Opinion / Op-Eds (`fa-comment-dots`), which legacy lumped together.
    """
    ctype = getattr(page, 'contenttype', '') or ''
    try:
        subtype = page.contentsubtype or ''
    except (AttributeError, ObjectDoesNotExist):
        subtype = ''
    if ctype == 'Event':
        return 'fa-calendar-alt'
    if ctype == 'Multimedia':
        return 'fa-headphones' if subtype == 'Audio' else 'fa-play-circle'
    if ctype == 'Publication':
        return 'fa-file-alt'
    if ctype == 'Opinion':
        if subtype in ('CIGI in the News', 'News Releases'):
            return 'fa-bullhorn'
        return 'fa-comment-dots'
    if ctype == 'Activity':
        return 'fa-globe'  # program/activity glyph on the type row (BugHerd #95)
    return ''


def type_of_content_data(page):
    """The type-of-content molecule's data: ``{'label', 'icon'}`` — the granular
    type label (``contentsubtype``) and its Font Awesome (light) glyph. Standalone
    so any module/card can render the molecule."""
    page = page.specific
    return {'label': _card_type_label(page), 'icon': _card_type_icon(page)}


def card_data(page, variant='media-vertical', pills=None, cta_label='Read More',
              cta_scheme='on-light', show_date=None,
              show_author=False, request=None):
    """Normalise a page into card render context.

    Base covers url + title + project pills (the `article-list-row` essentials).
    Media variants (see ``MEDIA_VARIANTS``) additionally get a feature image,
    serif excerpt, and a CTA. Person/event adapters extend this as those modules
    are built (avatar/role/expertise, date-stamp, datetime, etc.).

    Pass ``pills`` (a list of ``{'label', 'accent'}``) to override the page's own
    project pills; this also skips the `project_pills` query entirely — e.g. a
    module that locks cards to the program/context they're shown under.

    Note: media variants read ``image_feature``/``image_hero`` — consuming modules
    should ``select_related`` those in their ``get_context`` to avoid an N+1.
    """
    page = page.specific
    data = {
        'variant': variant,
        # get_url(request) → a relative path on the current site; the bare .url
        # property has no request and falls back to the Site's absolute root_url
        # (i.e. www.cigionline.org), which breaks links on localhost/staging.
        'url': page.get_url(request=request),
        'title': display_title(page),
        'pills': page_pills(page) if pills is None else pills,
    }
    if variant in MEDIA_VARIANTS:
        data['image'] = _card_image(page)
        data['excerpt'] = _card_excerpt(page)
        # Opinion-family articles render text-only in the bento side column
        # (BugHerd #120) — no thumb, title/type stack does the work.
        if variant == 'media-compact':
            article_type = getattr(page, 'article_type', None)
            if article_type is not None:
                from core.faceted_listing import OPINION_TYPE_SLUGS
                if article_type.slug in OPINION_TYPE_SLUGS:
                    data['image'] = None
        # cta_scheme picks the outline button colour scheme (on-light / on-dark)
        # — the button isn't surface-aware, so the consuming module sets it.
        data['cta'] = {'label': cta_label, 'url': data['url'], 'scheme': cta_scheme}
    if variant in ('media-compact', 'media-stacked', 'resource-feature', 'resource-compact'):
        data['type_label'] = _card_type_label(page)
        data['type_icon'] = _card_type_icon(page)
    if variant == 'event':
        # EventPage stores the start datetime in publishing_date (event_end holds
        # the end). The template formats it for the date-stamp + full date string.
        data['date'] = getattr(page, 'publishing_date', None)
        # Date-proximity chip (guide: Events Module): an event within 30 days
        # gets a quiet countdown chip — a signal of proximity, not a clock. The
        # number ticks into place on load (countdown.js).
        if data['date']:
            days_until = (timezone.localdate(data['date']) - timezone.localdate()).days
            if 0 <= days_until <= 30:
                data['days_until'] = days_until
    if variant == 'event-browse':
        # Events-listing browse card (1253:41198 / past 1253:41513): borderless —
        # pills · small grey date (no time) · title · excerpt · "RSVP >" (same
        # destination as the title, per whole-card single-intent). Past events
        # render the compact foot (bullet date left, RSVP right).
        data['excerpt'] = _card_excerpt(page)
        data['date'] = getattr(page, 'publishing_date', None)
        # RSVP only while registration is genuinely open (John, BugHerd #293):
        # future + registration_open + not private — the same gate as the event
        # hero's Register action. Everything else links as View Event.
        registration_gate = (
            getattr(page, 'registration_open', False)
            and not getattr(page, 'is_private_registration', False)
            and not (data['date'] and data['date'] < timezone.now())
        )
        data['cta'] = {'label': 'RSVP' if registration_gate else 'View Event',
                       'url': data['url'], 'scheme': cta_scheme}
        if data['date']:
            # One browse form for past and upcoming (BugHerd #463) — the old
            # is_past/compact_past fork picked the retired foot-row variant.
            days_until = (timezone.localdate(data['date']) - timezone.localdate()).days
            if 0 <= days_until <= 30:
                data['days_until'] = days_until
    if variant in ('resource-feature', 'resource-compact'):
        # Resource cards (Resource Carousel/Bento): pill(s) + date + title + serif
        # excerpt. One design, image optional — the feature gets a top image, the
        # compact omits it.
        data['excerpt'] = _card_excerpt(page)
        data['date'] = getattr(page, 'publishing_date', None)
        if variant == 'resource-feature':
            data['image'] = _card_image(page)
    # Byline options (Resource Bento AX, BugHerd #12): an author-set toggle
    # governs the date; author names (linked to their bio) show when the module
    # opts in. Date defaults on for the resource feature/compact and off for
    # media-compact — matching prior behaviour when a module passes nothing.
    if variant in ('resource-feature', 'resource-compact', 'media-compact', 'media-stacked'):
        if variant in ('media-compact', 'media-stacked'):
            data['date'] = getattr(page, 'publishing_date', None)
        data['show_date'] = (variant in ('resource-feature', 'resource-compact')) if show_date is None else show_date
        data['show_author'] = bool(show_author)
        if show_author:
            data['authors'] = _card_authors(page, request)
    return data

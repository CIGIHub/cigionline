"""CPT hero data layer.

Per-content-type hero presenters — the page-model-specific heroes (Article /
Opinion, Publication, Event, Person/Expert, Multimedia/Podcast, CIGI News). The
counterpart to ``core.cards`` for the hero region of each CPT page. Returns a
normalized context consumed by ``includes/heroes/*.html``.

These are STAGED (rendered on /ds-test-pages/heroes/ from real pages) and not yet
wired into the live page templates — that happens after design review. Type-
specific fields that aren't reliably modelled yet (publication number, event
speakers, podcast season/episode) are marked ``# QA:`` for wiring then.
"""

import html

from django.utils.html import strip_tags

from core.archive import archive_target
from core.cards import _card_excerpt, project_pills, social_icon, type_of_content_data  # noqa: F401

# The MultimediaSeriesPage slug of the Policy Prompt podcast. The static
# policy_prompt_logo_v2.png hero fallback applies to this series only —
# other series brand via their own image_logo, or carry no brand
# (BugHerd #312/#314).
POLICY_PROMPT_SERIES_SLUG = 'pp'


def _rel_url(page):
    """Relative public path for a page link. ``page.url`` has no request context
    here, so it falls back to the Site's absolute root_url (www.cigionline.org) —
    breaking links on localhost/staging. ``get_url_parts()[2]`` is the path only,
    independent of the request's host."""
    parts = page.get_url_parts() if hasattr(page, 'get_url_parts') else None
    return parts[2] if parts else getattr(page, 'url', '')


def _plain(value):
    """A rich-text or HTML field as plain text, safe to hand a template.

    strip_tags removes the markup but leaves entities alone, so an imported
    "Graphic &amp; Motion Designer" reached the template as literal "&amp;"
    and autoescape doubled it into "&amp;amp;" (Tim, BugHerd #366; the same
    defect core.cards fixed for card excerpts under BugHerd #406). Decode
    once here — the template re-escapes safely.
    """
    return html.unescape(strip_tags(str(value or ''))).strip()


def _breadcrumb(page):
    """Crumb trail for includes/breadcrumbs.html: "Home" first (the site root,
    labelled Home regardless of the page's title), then live ancestors. Each is
    {title, url, current}.

    The trail stops at two levels — the current page's own name is dropped, so a
    single event reads "Home > Events" (BugHerd #152). The name is kept only when
    Home is the sole ancestor; without it those pages (articles, opinions, person
    pages, which all sit directly under Home) would show a lone "Home".
    """
    crumbs = []
    for ancestor in page.get_ancestors().live().filter(depth__gt=1):
        if ancestor.depth == 2:
            crumbs.append({'title': 'Home', 'url': _rel_url(ancestor)})
        else:
            crumbs.append({'title': ancestor.title, 'url': _rel_url(ancestor)})
    if len(crumbs) < 2:
        crumbs.append({'title': page.title, 'current': True})
    return crumbs


def _ownership_crumbs(page):
    """The standardized content trail (IA decision 2026-08-26): Home > theme
    page > program page, through the page's first program that carries a
    ThemeProgram edge. Topic pages retire, so trails no longer route through
    topics or listing landings. Returns None when no tagged program is wired
    to a theme — the caller falls back to the archive trail
    (_content_crumbs)."""
    from research.models import ThemeProgram
    rel = getattr(page, 'projects', None)
    if rel is None:
        return None
    programs = list(rel.all())
    if not programs:
        return None
    edges = {e.program_id: e for e in
             ThemeProgram.objects.filter(program__in=programs)
             .select_related('theme')}
    for program in programs:
        edge = edges.get(program.pk)
        if edge and edge.theme.live and program.live:
            return [
                {'title': 'Home', 'url': '/'},
                {'title': edge.theme.title, 'url': _rel_url(edge.theme)},
                {'title': program.title, 'url': _rel_url(program)},
            ]
    return None


# Content singles that trail back to the archive when no current program owns
# them: IA decision 2026-09-04, CIGI aligned 2026-09-09 ("HOME -> Archive ->
# content"); BugHerd #279. Series, program, listing and basic pages keep their
# own trails.
ARCHIVE_TRAIL_TYPES = ('ArticlePage', 'PublicationPage', 'MultimediaPage', 'EventPage')


def _series_episode(page):
    """True for a MultimediaPage filed under a live MultimediaSeriesPage. It
    keeps the tree trail Home > <series> (Big Tech, Policy Prompt, Speaker
    Series). The tree parent decides, not the ``multimedia_series`` FK: 551
    videos under /multimedia/ carry an FK to an old video series."""
    parent = page.get_parent()
    return bool(parent and parent.live and
                parent.specific_class.__name__ == 'MultimediaSeriesPage')


def _archive_crumbs():
    """Home > <archive page title>, or None when no archive page resolves
    (core.archive: Settings -> Archive, else the auto-detected listing)."""
    target = archive_target()
    if not target:
        return None
    return [{'title': 'Home', 'url': '/'},
            {'title': target['title'], 'url': target['url']}]


def _content_crumbs(page):
    """The trail for every content-style hero (BugHerd #279):
    1. Home > theme > program when a current program owns the page;
    2. Home > <archive> for an article / publication / multimedia / event no
       current program owns (a series episode keeps Home > <series>);
    3. else the tree walk.
    Never a topic: topic pages retired (IA 2026-08-26), and the topic crumb
    that linked their unstyled pages is gone."""
    owned = _ownership_crumbs(page)
    if owned:
        return owned
    cls = page.__class__.__name__
    if cls in ARCHIVE_TRAIL_TYPES and not (cls == 'MultimediaPage' and _series_episode(page)):
        archive = _archive_crumbs()
        if archive:
            return archive
    return _breadcrumb(page)


def _experts_listing_page():
    """The Experts listing page, or None.

    The target follows the primary nav's own Experts link, so an editor who
    repoints that item moves the crumb with it. Matched on page type, not on the
    item's label, which an editor may rename. Falls back to the live listing.
    """
    from menus.models import MenuItem
    from people.models import PersonListPage

    return next(
        (item.link_page.specific for item in MenuItem.objects.filter(
            menu__slug='primary-nav', link_page__isnull=False,
        ).select_related('link_page')
         if item.link_page.live
         and isinstance(item.link_page.specific, PersonListPage)),
        None,
    ) or PersonListPage.objects.live().first()


def _experts_listing_crumb():
    """The Experts listing as a breadcrumb entry, or None. Person pages sit
    directly under Home, so their trail names the listing rather than themselves
    (BugHerd #208). The crumb is a link: the person's page is the current page,
    not this one."""
    listing = _experts_listing_page()
    if not listing:
        return None
    return {'title': 'Experts', 'url': _rel_url(listing)}


def _expert_role_crumb(type_id):
    """Home > <role> for a CIGI expert role (Research Directors, Distinguished
    Fellows, Senior Fellows, Fellows): the Experts listing with its Type facet
    pre-selected to that role, labelled as the facet labels it. Falls back to
    the plain listing when the page has no faceted listing to read a prefix
    from. None without a listing page at all."""
    from core.faceted_listing import EXPERT_ROLE_LABELS, default_listing_prefix
    listing = _experts_listing_page()
    if not listing:
        return None
    url = _rel_url(listing)
    prefix = None
    try:
        for block in listing.specific.body.raw_data:
            value = block.get('value', {})
            if block.get('type') == 'faceted_listing' and value.get('card_type') == 'expert':
                prefix = value.get('prefix') or default_listing_prefix(value)
                break
    except Exception:  # no body / other listing shapes: the plain listing suffices
        pass
    if prefix:
        # The fragment is the router's anchor (faceted_listing_block.html renders
        # id="router-<prefix>"); router.js lands on it so the reader sees the
        # filtered roles, not the page top (Tia, BugHerd #516). Same contract
        # as the topic pill deep links (core.router_links).
        url = '%s?%s-type=%s#router-%s' % (url, prefix, type_id, prefix)
    return {'title': EXPERT_ROLE_LABELS[type_id], 'url': url}


def _tab_listing_url(page, card_type, person_type=None):
    """``<page url>?tab=<slug>`` for the composable tab on ``page`` whose faceted
    listing matches ``card_type`` (and ``person_type`` when given), so an
    authored tab-label change moves the link rather than breaking it. The URL
    ends in the listing's ``#router-<prefix>`` anchor so the reader lands on
    the listing, not the page top (BugHerd #516). The bare page URL when no tab
    matches."""
    from streams.blocks import _slugify_label
    from core.faceted_listing import default_listing_prefix
    page_url = _rel_url(page)
    try:
        for block in page.specific.body.raw_data:
            if block.get('type') != 'composable_tabs':
                continue
            used = set()
            for tab in block.get('value', {}).get('tabs', []):
                # ListBlock items nest their struct under 'value'.
                tab = tab.get('value', tab) if isinstance(tab, dict) else tab
                slug = _slugify_label(tab.get('label'), used)
                for child in tab.get('content', []):
                    value = child.get('value', {})
                    # card_type must gate the match: EVERY faceted listing
                    # stores a person_type value (the field default), so a
                    # publications listing matches person_type alone.
                    # A blank person_type means the block default, dph_fellow —
                    # the same fallback resolve_scope applies. Staging's cohort
                    # listing stores '' and the crumb fell back to the page top.
                    listing_type = value.get('person_type') or 'dph_fellow'
                    if (child.get('type') == 'faceted_listing'
                            and value.get('card_type') == card_type
                            and (person_type is None or listing_type == person_type)):
                        prefix = value.get('prefix') or default_listing_prefix(value)
                        return '%s?tab=%s#router-%s' % (page_url, slug, prefix)
    except Exception:  # authored-body shapes vary; the plain page link suffices
        pass
    return page_url


def _dph_crumbs(person_type, label):
    """Home > Digital Policy Hub > <label>, the last crumb deep-linking the hub
    tab whose people listing is scoped to ``person_type`` (dph_fellow →
    Cohort, BugHerd #342; dph_speaker → Speakers, BugHerd #361). None when
    the hub page is missing."""
    from wagtail.models import Page
    hub = Page.objects.live().filter(slug='digital-policy-hub').first()
    if not hub:
        return None
    return [
        {'title': 'Home', 'url': '/'},
        {'title': hub.title, 'url': _rel_url(hub)},
        {'title': label, 'url': _tab_listing_url(hub, 'person', person_type)},
    ]


def _leadership_crumbs(label, card_type, person_type=None):
    """Home > <label>, linking the Leadership page tab whose listing matches
    ``card_type`` / ``person_type``: Staff → the Staff Directory tab (BugHerd
    #361); Board of Directors / Senior Management → the Senior Management and
    Board of Directors tab (BugHerd #527). None when that page is missing; the
    bare Leadership page when the tab is (as _tab_listing_url, and #361)."""
    from wagtail.models import Page
    leadership = Page.objects.live().filter(slug='leadership-partners-and-team').first()
    if not leadership:
        return None
    return [
        {'title': 'Home', 'url': '/'},
        {'title': label, 'url': _tab_listing_url(leadership, card_type, person_type)},
    ]


def _person_role_crumbs(person):
    """A person's trail from their role, not a blanket "Experts" (Tim, BugHerd
    #361 — the CFO trailed to Experts). Person types decide, in this order
    for the multi-type people (Evan, 2026-09-17):

      1. Digital Policy Hub Fellow  → Home > Digital Policy Hub > Cohort (#342)
      2. Board Member, then         → Home > <Board of Directors | Senior
         Management Team              Management>, the Leadership page's Senior
                                      Management and Board of Directors tab (#527)
      3. an expert role             → Home > <Research Directors | Distinguished
                                      Fellows | Senior Fellows | Fellows>, the
                                      Experts listing filtered to that role
      4. Staff                      → Home > Staff, the Leadership page's Staff
                                      Directory tab
      5. Speaker / DPH Speaker      → Home > Digital Policy Hub > Speakers
      6. everyone else              → Home > Experts (#208), the fallback for
                                      the external-profile and untyped majority

    Returns None when nothing above resolves, so the caller can fall back to
    the generic tree trail."""
    from core.faceted_listing import EXPERT_ROLE_TYPE_IDS
    types = list(person.person_types.values_list('id', 'name'))
    names = {name for _, name in types}
    ids = {type_id for type_id, _ in types}

    if 'Digital Policy Hub Fellow' in names:
        crumbs = _dph_crumbs('dph_fellow', 'Cohort')
        if crumbs:
            return crumbs
    # Board members and senior management trailed to Experts, a listing that
    # doesn't carry them (John, BugHerd #527). Their role outranks an expert
    # role: the senior managers who are also Research Directors read as
    # Senior Management. No type filter on the link — that listing's Role
    # facet leaves both types out, so the reader couldn't see or clear it.
    for name, label in (('Board Member', 'Board of Directors'),
                        ('Management Team', 'Senior Management')):
        if name in names:
            crumbs = _leadership_crumbs(label, 'person', 'management_board')
            if crumbs:
                return crumbs
    for type_id in EXPERT_ROLE_TYPE_IDS:  # ordered senior → junior
        if type_id in ids:
            crumb = _expert_role_crumb(type_id)
            if crumb:
                return [{'title': 'Home', 'url': '/'}, crumb]
    if 'Staff' in names:
        crumbs = _leadership_crumbs('Staff', 'staff')
        if crumbs:
            return crumbs
    if names & {'Speaker', 'DPH Speaker'}:
        crumbs = _dph_crumbs('dph_speaker', 'Speakers')
        if crumbs:
            return crumbs
    experts = _experts_listing_crumb()
    return [{'title': 'Home', 'url': '/'}, experts] if experts else None


def _pill_accent(item):
    """Theme accent for a topic or program pill, defaulting neutral grey when
    unmapped (BugHerd #326; mapping per BugHerd #205).
    Topics map via ``program_theme``; programs via ThemeProgram."""
    from core.cards import _project_accent, topic_accent
    if hasattr(item, 'program_theme'):
        return topic_accent(item)
    return _project_accent(item) or 'grey'


def _topic_eyebrow(page):
    """The italic topic/program links above the title. Topics first; falls back to
    the page's current-IA programs. Each is a link (label + url), not a pill."""
    items = []
    topics = getattr(page, 'topics', None)
    source = topics.all() if topics is not None else []
    if not source:
        # Theme-mapped programs only — project_pills' legacy-dropping rule
        # (Tim, BugHerd #326), which the ownership trail follows too: a legacy
        # program drew a grey pill naming a retired initiative beside its
        # successor (Tim, BugHerd #514 — "Space Governance 4.0" next to
        # "Space Governance"). Nothing current left → no pill row, as on cards.
        return [{'title': p['label'], 'url': p['url'], 'accent': p['accent']}
                for p in project_pills(page)]
    for t in source:
        # Each topic/program carries its theme accent, so the hero pills match
        # the same tag everywhere else on the site (BugHerd #205 — they were
        # hardcoded red in the template).
        items.append({'title': t.title, 'url': _rel_url(t), 'accent': _pill_accent(t)})
    return items


def _byline_person(person):
    """One hero-byline credit: name + bio link (BugHerd #324 — Juode: the
    byline "can be" clickable, "across all template pages"). Archived or
    unrouted people keep a plain-text name, like the reading rail."""
    url = None
    if person.live and not getattr(person.specific_deferred, 'archive', 1):
        # Relative path, not .url — bare .url emits the prod host off-prod.
        parts = person.get_url_parts()
        url = parts[2] if parts else None
    return {'name': person.title, 'url': url}


def _author_names(page):
    """Author byline credits ({name, url} dicts) for the hero. The authors
    relation leads — it carries the person pages the names link to; the
    author_names property is just its titles (core.models), so preferring it
    would strip every link."""
    authors = getattr(page, 'authors', None)
    if authors is not None:
        out = []
        for rel in authors.all():
            person = getattr(rel, 'author', None)
            if person:
                out.append(_byline_person(person))
        if out:
            return out
    # Plain-text credit line fallback — no person pages to link.
    return [{'name': n, 'url': None} for n in (getattr(page, 'author_names', None) or [])]


def _editor_names(page):
    """Editor byline credits — the hero byline's fallback when a page has no
    authors (edited works / books credit their editors instead)."""
    rel = getattr(page, 'editors', None)
    if rel is None or not hasattr(rel, 'all'):
        return []
    out = []
    for e in rel.all():
        person = getattr(e, 'editor', None)
        if person:
            out.append(_byline_person(person))
    return out


def _share_links(page):
    """Share-this-page intents (X + LinkedIn) for the hero's Share/Follow row."""
    url = getattr(page, 'full_url', None) or page.url
    return [
        {'platform': 'twitter', 'url': f'https://twitter.com/intent/tweet?url={url}'},
        {'platform': 'linkedin', 'url': f'https://www.linkedin.com/sharing/share-offsite/?url={url}'},
    ]


def _audio_source(page):
    """Resolve the hero audio source (option C — hybrid):
    - a self-hosted audio FILE (our media, audio extension) → DS Plyr player;
    - a third-party platform URL (Simplecast/SoundCloud/etc.) → Wagtail ``{% embed %}``
      (oEmbed), since those can't be played/skinned as a native <audio>.
    Returns ``{'type': 'file', 'src': url}`` | ``{'type': 'embed', 'url': url}`` | None.
    """
    # 1. Self-hosted upload (ArticlePage.audio_file — the opinion TTS mp3).
    f = getattr(page, 'audio_file', None)
    if f:
        try:
            return {'type': 'file', 'src': f.url}
        except Exception:
            pass
    # 2. Platform-hosted: the oEmbed-able URL the legacy site embeds. Prefer
    #    multimedia_url (what {% embed %} resolves); podcast_audio_url is a
    #    non-hotlinkable cdn file (403) so it's only used if it's a real file URL.
    url = getattr(page, 'multimedia_url', '') or getattr(page, 'podcast_audio_url', '') or ''
    if not url:
        return None
    # Extension test on the path only — cdn URLs carry querystrings
    # (…/default_tc.mp3?nocache) that defeated a plain endswith().
    path = url.lower().split('?', 1)[0].split('#', 1)[0]
    if path.endswith(('.mp3', '.m4a', '.ogg', '.wav', '.aac')):
        # A direct audio file can never oEmbed — {% embed %} raises
        # EmbedUnsupportedProviderException and renders an empty hero slot
        # (26 live episodes, all cdn.simplecast.com). Those files serve with
        # Range support and no hotlink guard, so the native player takes
        # every file URL regardless of host.
        return {'type': 'file', 'src': url}
    return {'type': 'embed', 'url': url}


def _apply_content_toggles(page, data):
    """Drop content-hero sections the author switched off (HeroContentTogglesAbstract
    `show_hero_*`, default on; the banner is opt-in on events and publications).
    Templates render each section only when its data is
    present, so zeroing the data here hides it — no template branching needed."""
    if not getattr(page, 'show_hero_banner', True):
        data['banner'] = False
    if not getattr(page, 'show_hero_topics', True):
        data['eyebrow'] = []
    if not getattr(page, 'show_hero_excerpt', True):
        data['excerpt'] = ''
    if not getattr(page, 'show_hero_byline', True):
        data['authors'] = []
    if not getattr(page, 'show_hero_date', True):
        data['date'] = None
    if not getattr(page, 'show_hero_share', True):
        data['share'] = []
    if not getattr(page, 'show_hero_action', True):
        data['action'] = None
        data['actions'] = None  # the per-type Register row (events) hides with the action
        data['audio'] = None
        data['location'] = ''
    return data


def _base(page, layout, simple):
    """Fields common to every content-style hero."""
    type_data = type_of_content_data(page)
    data = {
        'layout': layout,
        'simple': simple,
        # Standardized trail: Home > theme > program where the ownership chain
        # resolves, else Home > <archive> for content singles (BugHerd #279),
        # else the tree walk.
        'breadcrumb': _content_crumbs(page),
        'eyebrow': [] if simple else _topic_eyebrow(page),
        'type_label': type_data['label'],
        'type_icon': type_data['icon'],
        'title': page.title,
        'authors': _author_names(page),
        'excerpt': '' if simple else _card_excerpt(page),
        'date': getattr(page, 'publishing_date', None),
        'image': getattr(page, 'image_hero', None),
        'banner': True,          # show image_hero as a full-bleed top banner
        'share': _share_links(page),
        # Label the row on every content hero (Tia, BugHerd #449 — unlabelled
        # icons under a byline read as the AUTHOR's accounts, not share links).
        # CIGI News got this first under BugHerd #469; the reasoning was never
        # news-specific, so it now applies to publications, events and video too.
        'share_heading': 'Share',
        'url': _rel_url(page),
        'meta': [],
        'location': '',
        'audio': None,           # {'type':'file','src'} (DS player) | {'type':'embed','url'} (oEmbed)
        'action': None,
    }
    # Byline fallback: authors win; when a page has none, credit its editors
    # ("Edited by …" in the template). Editors are only queried in that case.
    data['byline_editors'] = [] if data['authors'] else _editor_names(page)
    return data


def article_hero_data(page, simple=False):
    """Article / Opinion / CIGI News / In the News hero (content layout).
    Opinion: banner + topic pills + "listen to article" native audio. News / In
    the News: no banner, "Follow" heading; In the News adds an external
    "Read the full article" action.
    """
    page = page.specific
    data = _base(page, 'content', simple)
    # Series-skin banner: legacy series theme forks used the article's
    # image_banner as the hero image — it wins over image_hero where authored
    # (237 live articles; Evan 2026-07-08).
    data['image'] = getattr(page, 'image_banner', None) or data['image']
    try:
        subtype = page.contentsubtype or ''
    except Exception:
        subtype = ''
    # CIGI News + In the News drop the banner; opinions keep it.
    # (article_type.title carries "... News ..." for those types.) The "Share"
    # label they gained under BugHerd #469 is now the base default — see _base.
    is_news = 'News' in subtype
    if is_news:
        data['banner'] = False
    # The In the News reading shell adds the "following is an excerpt" note
    # itself (article_page.html). 60 imported pages also carry that sentence
    # as their short_description, so the hero excerpt repeated it above the
    # body (John + Tia, BugHerd #362). Drop the excerpt when it IS the note.
    if subtype == 'CIGI in the News' and \
            data['excerpt'].lower().startswith('the following is an excerpt'):
        data['excerpt'] = ''
    # Essays never show short_description in the hero (Tia, BugHerd #502).
    # _card_excerpt reads feature_subtitle, then subtitle, then
    # short_description; an essay with either subtitle keeps it, the rest go
    # without. 177 of 296 live essays fall to no excerpt.
    if subtype == 'Essays' and not (getattr(page, 'feature_subtitle', '')
                                    or getattr(page, 'subtitle', '')):
        data['excerpt'] = ''
    # Opinion "listen to article" → the generated TTS file in `audio_file`
    # (FileField; 65 live articles, ~all opinions). Fall back to the platform
    # audio resolver for any legacy multimedia_url case.
    if not is_news and not simple:
        audio_file = getattr(page, 'audio_file', None)
        if audio_file:
            data['audio'] = {'type': 'file', 'src': audio_file.url}
        else:
            data['audio'] = _audio_source(page)
        # The TTS player stays reachable while reading (Yang, BugHerd #298):
        # the pinbar docks a compact play control. File players only — the
        # embed fallback can't be driven from outside its iframe.
        if data.get('audio') and data['audio'].get('type') == 'file':
            data['sticky_meta'] = True
    # In the News links out to the original publisher. Mirror the live template's
    # gate (article_type.title == 'CIGI in the News') + authorable button label.
    external = getattr(page, 'website_url', '') or ''
    if subtype == 'CIGI in the News' and external:
        label = getattr(page, 'website_button_text', '') or 'Read the full article'
        data['action'] = {'label': label, 'url': external,
                           'icon': 'fa-arrow-up-right-from-square', 'external': True, 'style': 'solid'}
    return _apply_content_toggles(page, data)


def publication_hero_data(page, simple=False):
    """Publication hero — type icon + number meta + author + Download."""
    page = page.specific
    data = _base(page, 'content', simple)
    # The trail comes from _base: #236's topic crumb is retired with the topic
    # pages, so an untagged publication trails to the archive (BugHerd #279).
    # Publications store the landscape hero banner in `image_feature` (75% live),
    # not `image_hero` (0%) — mirror the card's image preference. Without this the
    # publication hero banner is empty for every publication.
    data['image'] = getattr(page, 'image_feature', None) or data['image']
    # Anti-upscale guard: the banner renders full-bleed (fill-2400x800). Many
    # older publications only have a small thumbnail in image_feature (302x150
    # etc.), which upscales into an artifact-y banner. Skip the banner unless
    # the source is at least the content width — a too-small source is better
    # shown as no banner than a blurry one.
    img = data.get('image')
    if img is not None and getattr(img, 'width', 0) < 1280:
        data['banner'] = False
    # "Policy Brief No. 240"-style type + number is the existing `subtitle`
    # field (~96% of authored subtitles are exactly that line) — no new field.
    # Rendered as the uppercase kicker above the title per Kay's hero mock
    # (BugHerd #461); the legacy hero showed the same field as an <h2>.
    data['kicker'] = '' if simple else _plain(page.subtitle)
    # The publication's own PDF is pdf_downloads[0] — the supporting-materials
    # tag deliberately skips it as "the hero download" (cards.py); the book
    # excerpt is the books-only fallback. No download → no action (a self-link
    # button is worse than no button).
    # Every authored PDF is a hero button, not just the first (Tim, BugHerd
    # #474 — the French edition sat inside the Supporting Materials drawer).
    # pdf_downloads holds the publication's OWN file in its various editions;
    # Supporting Materials is for the other documents attached to the page.
    # The first PDF keeps the solid "Download"; the rest are outline buttons
    # carrying the label the author gave them. `display` gates the EXTRAS only:
    # nothing honoured it before, and applying it to the first PDF would strip
    # the only download from two live publications that carry display=False.
    # Widening it is a separate call, not this ticket's.
    all_pdfs = [b for b in (getattr(page, 'pdf_downloads', None) or [])
                if b.value.get('file')]
    pdfs = all_pdfs[:1] + [b for b in all_pdfs[1:] if b.value.get('display', True)]
    actions = []
    for index, block in enumerate(pdfs):
        doc = block.value['file']
        label = (block.value.get('button_text') or '').strip()
        actions.append({
            'label': label or ('Download' if index == 0 else 'Download PDF'),
            'url': doc.url, 'icon': 'fa-arrow-down-to-line',
            'style': 'solid' if index == 0 else 'outline',
        })
    if not actions:
        excerpt_doc = getattr(page, 'book_excerpt_download', None)
        if excerpt_doc:
            actions.append({'label': 'Download', 'url': excerpt_doc.url,
                            'icon': 'fa-arrow-down-to-line', 'style': 'solid'})
    if actions:
        data['actions'] = actions
        data['action'] = actions[0]  # every other hero still reads one action
    # No short-description excerpt on any publication hero: the body paragraph
    # opens with the same copy, so the page read the same text twice. DPH
    # Working Papers dropped it first (Jennifer, BugHerd #441); Tia widened the
    # rule to every publication (BugHerd #502). short_description still feeds
    # the meta/og description tags.
    data['excerpt'] = ''
    # DPH Working Papers carry the hub's green accent on the hero chrome
    # (buttons/rules) per the 1595 DPH frames.
    if getattr(getattr(page, 'publication_type', None), 'slug', '') == 'working-paper':
        data['accent'] = 'green'
    return _apply_content_toggles(page, data)


def publication_book_hero_data(page, simple=False):
    """Books publication hero — the standard publication hero PLUS book-only data
    (cover · editors · publication metadata · excerpt download · purchase links),
    rendered by the ds-hero__book region in content_hero.html. Placement + look
    are provisional (no book-hero design yet) — iterated in QA."""
    from django.template.defaultfilters import date as date_filter

    page = page.specific
    data = publication_hero_data(page, simple)
    purchase = []
    for b in getattr(page, 'book_purchase_links', []) or []:
        purchase.append({'label': b.value.get('link_text'), 'url': b.value.get('url')})
    # Editors are credited in the hero byline (via _base's byline fallback),
    # not in this region.
    # Publication metadata as label/value rows — only the fields that are set,
    # mirroring the legacy .publication-book-metadata list.
    meta = []
    if getattr(page, 'isbn', ''):
        meta.append({'label': 'ISBN', 'value': page.isbn})
    if getattr(page, 'isbn_ebook', ''):
        meta.append({'label': 'eBook ISBN', 'value': page.isbn_ebook})
    if getattr(page, 'isbn_hardcover', ''):
        meta.append({'label': 'Hardcover ISBN', 'value': page.isbn_hardcover})
    if getattr(page, 'book_publisher', ''):
        meta.append({'label': 'Publisher', 'value': page.book_publisher,
                     'url': getattr(page, 'book_publisher_url', '')})
    if getattr(page, 'publishing_date', None):
        meta.append({'label': 'Published', 'value': date_filter(page.publishing_date, 'F j, Y')})
    if getattr(page, 'book_pages', None):
        meta.append({'label': 'Pages', 'value': page.book_pages})
    if getattr(page, 'book_format', ''):
        meta.append({'label': 'Format', 'value': page.get_book_format_display()})
    excerpt = getattr(page, 'book_excerpt_download', None)
    data['book'] = {
        'cover': getattr(page, 'image_cover', None),
        'meta': meta,
        'excerpt_url': excerpt.file.url if excerpt else '',
        'purchase_links': purchase,
    }
    return data


def _event_type_line(page):
    """"Public Event: Signature Lecture (Hybrid)" — the registration hero's
    single meta line (Event Form 1705:20340). Each part is optional."""
    access = page.get_event_access_display() if page.event_access is not None else ''
    kind = page.get_event_type_display() if getattr(page, 'event_type', '') else ''
    fmt = page.get_event_format_display() if getattr(page, 'event_format', '') else ''
    line = f'{access} Event' if access else ''
    if kind:
        line = f'{line}: {kind}' if line else kind
    if fmt:
        line = f'{line} ({fmt})' if line else fmt
    return line


def event_hero_data(page, simple=False, invite=None, variant=None):
    """Event hero — prominent date (calendar) at top, type, speakers, location,
    Register action. ``invite`` (from EventPage.serve's session handling) lets
    private-registration events surface the on-site Register action.
    ``variant='registration'`` is the dark hero of the on-site registration
    pages (Event Form 1705:20340): date stamp beside the title, one
    access/type/format line, byline · date · location aside; no breadcrumb,
    pills, excerpt, Register action or pin-bar."""
    page = page.specific
    if variant == 'registration':
        return _event_registration_hero_data(page)
    data = _base(page, 'content', simple)
    if getattr(page, 'event_type', ''):
        data['meta'].append(page.get_event_type_display() if hasattr(page, 'get_event_type_display') else page.event_type)
    # Venue name when set; else the full address (location_string joins the
    # address fields for in-person/hybrid events). Physical addresses get a
    # maps link — legacy hero parity; fixes the dropped-location regression.
    address = page.location_string() if callable(getattr(page, 'location_string', None)) else ''
    data['location'] = getattr(page, 'location_name', '') or address
    if address:
        data['location_url'] = page.location_map_url()
    # On-site registration wins over the external registration_url. Private
    # events show it only with an invite (token carried into the flow).
    is_past = page.is_past() if callable(getattr(page, 'is_past', None)) else False
    onsite = (getattr(page, 'registration_open', False) and not is_past
              and (not getattr(page, 'is_private_registration', False) or invite))
    reg_url = getattr(page, 'registration_url', '') or getattr(page, 'website_url', '') or ''
    # Register is the outline treatment in the event frame (1360:114601) —
    # red label + chevron, not the solid fill.
    if onsite:
        # One button per open registration type ("In Person", "Virtual" —
        # Event Template 1705:20640), each deep-linking to that type's form.
        # The type list is the chooser's own (EventPage.open_registration_types),
        # so staff-only and closed types stay hidden here too. With no
        # resolvable type the single Register keeps pointing at register/,
        # which renders the no-types page.
        token = f'?invite={invite.token}' if invite else ''
        types = page.open_registration_types(invite) if hasattr(page, 'open_registration_types') else []
        if types:
            base = _rel_url(page) + 'register/type/'
            # Labels (client, 2026-09-17): several types read "Register: <type>";
            # a single type reads "Register" — or the authorable registration_text,
            # which stays the editor's manual copy control for a lone button.
            if len(types) > 1:
                data['actions'] = [{'label': f'Register: {t.name}', 'url': f'{base}{t.slug}/{token}',
                                    'style': 'outline'} for t in types]
            else:
                data['action'] = {'label': getattr(page, 'registration_text', '') or 'Register',
                                  'url': f'{base}{types[0].slug}/{token}', 'style': 'outline'}
        else:
            data['action'] = {'label': getattr(page, 'registration_text', '') or 'Register Now',
                              'url': _rel_url(page) + 'register/' + token, 'style': 'outline'}
    elif reg_url and not is_past:
        # Legacy hero parity: past events never show Register — 269 live past
        # events still carry stale external registration_url values.
        data['action'] = {'label': getattr(page, 'registration_text', '') or 'Register Now',
                          'url': reg_url, 'style': 'outline'}
    # Speakers ARE the `authors` relation — EventPage surfaces it under a
    # "Speakers" InlinePanel; the byline from _base(authors) is correct.
    # No share/follow group on the event hero (1360:114601) — the aside is
    # byline · date · location only.
    data['share'] = []
    # Events pin a condensed title · date · location bar once the hero scrolls
    # out of view (BugHerd #202, hero-pinbar.js).
    data['sticky_meta'] = True
    return _apply_content_toggles(page, data)


def _event_registration_hero_data(page):
    """The registration pages' dark hero (Event Form 1705:20340). Built on the
    content anatomy so the byline/date/location aside and the reading-rail
    geometry are the event single's own; only the presentation flags differ."""
    data = _base(page, 'content', simple=True)
    data.update({
        'surface': 'dark',
        'breadcrumb': [],
        'banner': False,          # the frame has no image banner
        'date_stamp': True,       # red month/day circle beside the title
        'meta': [],
        # The access/type/format line sits in the aside under the date (1705:20386).
        'aside_meta': [m for m in [_event_type_line(page)] if m],
        'share': [],
        'action': None,
        'actions': None,
        'sticky_meta': False,     # no pin-bar on the flow pages
        'is_registration': True,
    })
    address = page.location_string() if callable(getattr(page, 'location_string', None)) else ''
    data['location'] = getattr(page, 'location_name', '') or address
    if address:
        data['location_url'] = page.location_map_url()
    return data


def podcast_hero_data(page, simple=False):
    """Multimedia / Podcast hero — branded two-column: title + player on the left,
    cover art + season/episode + byline + Share/Subscribe/Follow on the right."""
    page = page.specific
    data = _base(page, 'podcast', simple)
    data['is_podcast'] = True
    # Cover art (right column, above the episode meta — frames 1639:76669 /
    # 1312:31660). Most episodes author only image_hero, so it's the fallback.
    data['cover'] = (getattr(page, 'image_square', None)
                     or getattr(page, 'image_poster', None)
                     or getattr(page, 'image_hero', None))
    data['audio'] = _audio_source(page)
    # Season/episode numbering meta ("#<episode> · SEASON <n>").
    episode = getattr(page, 'podcast_episode', None)
    season = getattr(page, 'podcast_season', None)
    meta_parts = []
    if episode:
        meta_parts.append(f'#{episode}')
    if season:
        meta_parts.append(f'SEASON {season}')
    if meta_parts:
        data['meta'] = [' › '.join(meta_parts)]
    # Series branding: the episode's own series logo (image_logo — authorable
    # per series, e.g. Big Tech). The static Policy Prompt logo in the hero
    # template is a fallback for the Policy Prompt series ONLY — legacy
    # episodes (no series, or a series without a logo) carry no brand
    # (BugHerd #312/#314, Tim).
    series = getattr(page, 'multimedia_series', None)
    series = series.specific if series is not None else None
    data['logo'] = getattr(series, 'image_logo', None) if series else None
    data['is_policy_prompt'] = bool(
        series is not None and series.slug == POLICY_PROMPT_SERIES_SLUG)
    # The hero shell follows the page surface: PP pink, everything else light
    # (BugHerd #312 — ds_surface is the single source of truth).
    data['surface'] = getattr(page, 'ds_surface', 'pink')
    data['subscribe'] = []
    data['follow'] = []
    if series is not None:
        for b in getattr(series, 'podcast_subscribe_buttons', []) or []:
            # platform = the authored label, so share_buttons can resolve a
            # brand glyph ('Apple Podcasts', 'Spotify'); unknown platforms
            # render as text links.
            data['subscribe'].append({
                'label': b.value.get('label'),
                'platform': b.value.get('label'),
                'url': b.value.get('url'),
            })
        # Follow = the series' social accounts (share_buttons maps platform→icon).
        for b in getattr(series, 'podcast_follow_buttons', []) or []:
            data['follow'].append({'platform': b.value.get('platform'), 'url': b.value.get('url')})
    _apply_content_toggles(page, data)
    # Podcast-only section toggles (HeroPodcastTogglesAbstract).
    if not getattr(page, 'show_hero_logo', True):
        data['logo'] = None
    if not getattr(page, 'show_hero_cover', True):
        data['cover'] = None
    if not getattr(page, 'show_hero_meta', True):
        data['meta'] = []
    if not getattr(page, 'show_hero_subscribe', True):
        data['subscribe'] = []
    if not getattr(page, 'show_hero_follow', True):
        data['follow'] = []
    return data


def theme_hero_data(page, simple=False):
    """Research-theme hero (Theme page): title + description on the
    theme's accent surface; no banner/byline — themes are taxonomy, not content."""

    page = page.specific
    return {
        'layout': 'content',
        'simple': simple,
        'breadcrumb': _breadcrumb(page),
        'eyebrow': [],
        'type_label': '', 'type_icon': None,
        'title': page.title,
        'authors': [],
        'excerpt': _plain(page.description),
        'date': None,
        'image': None,
        'banner': False,
        'share': [],
        'share_heading': '',
        'url': _rel_url(page),
        'meta': [],
        'location': '',
        'audio': None,
        'action': None,
        'accent': page.accent_colour,
    }


def project_hero_data(page, simple=False):
    """Program / activity hero (ProjectPage): title + subtitle on the owning
    theme's accent surface (first ThemeProgram membership — the same edge the
    program card pills read; red fallback). The legacy hero's `image_banner`
    renders as the full-bleed top banner where authored."""
    page = page.specific
    membership = page.theme_memberships.select_related('theme').first()
    banner = getattr(page, 'image_banner', None)
    # Standardized trail (IA 2026-08-26, supersedes #341's Topics crumb):
    # Home > theme — the program itself is the current page and drops per
    # #152. The tree walk can't surface the owning theme (BugHerd #88), so
    # the ThemeProgram edge supplies it.
    crumbs = [c for c in _breadcrumb(page) if c.get('title') == 'Home']
    if membership:
        crumbs.append({'title': membership.theme.title, 'url': _rel_url(membership.theme)})
    return {
        'layout': 'content',
        'simple': simple,
        'breadcrumb': crumbs,
        'eyebrow': [],
        'type_label': '', 'type_icon': None,
        'title': page.title,
        'authors': [],
        'excerpt': _plain(page.subtitle),
        'date': None,
        'image': banner,
        'banner': bool(banner),
        'share': [],
        'share_heading': '',
        'url': _rel_url(page),
        'meta': [],
        'location': '',
        'audio': None,
        'action': None,
        'accent': membership.theme.accent_colour if membership else 'red',
    }


def is_dph_subtree(page):
    """True for the Digital Policy Hub page and anything under it. The hub runs
    charcoal with the green accent (BugHerd #166/#168), and both the page chrome
    and the fallback hero read this, so the test lives in one place."""
    url_path = getattr(page, 'url_path', '') or ''
    return '/digital-policy-hub/' in url_path or url_path.endswith('/digital-policy-hub')


def basic_hero_data(page, simple=False):
    """BasicPage hero (about-section / informational pages): breadcrumb ·
    title · subtitle as excerpt on the default surface. DS-composed BasicPages
    that open with an authored hero module (split/primary/alt hero) skip this
    entirely — the template gates on `starts_with_hero`."""
    page = page.specific
    # The DPH subtree runs charcoal/green, so the fallback hero has to follow it.
    # Left on the default light/red it landed as a white band with a red
    # breadcrumb inside the charcoal page.
    dph = is_dph_subtree(page)
    return {
        'layout': 'content',
        'simple': simple,
        'breadcrumb': _breadcrumb(page),
        'eyebrow': [],
        'type_label': '', 'type_icon': None,
        'title': page.title,
        'authors': [],
        'excerpt': _plain(page.subtitle),
        'date': None,
        'image': None,
        'banner': False,
        'share': [],
        'share_heading': '',
        'url': _rel_url(page),
        'meta': [],
        'location': '',
        'audio': None,
        'action': None,
        # Follow the page's authored surface (thank-you pages run dark; the
        # light-defaulted hero sat as a white band on the dark page — Tia,
        # BugHerd #462). DPH keeps its charcoal override.
        'surface': 'charcoal' if dph else (getattr(page, 'surface', '') or ''),
        'accent': 'green' if dph else 'red',
    }


def listing_hero_data(page, simple=False):
    """Router-landing hero (Events / Experts / Annual Reports / Opinions):
    breadcrumb · title · subtitle on the default surface. Same shape as the
    BasicPage hero — a listing has no byline, date, type label or share row.
    Composed pages that open with an authored hero module, or that carry an
    `image_hero` (the alt-hero treatment), skip this: their templates gate on
    `starts_with_hero` / `image_hero` before calling it."""
    page = page.specific
    return {
        'layout': 'content',
        'simple': simple,
        'breadcrumb': _breadcrumb(page),
        'eyebrow': [],
        'type_label': '', 'type_icon': None,
        'title': page.title,
        'authors': [],
        'excerpt': _plain(getattr(page, 'subtitle', '')),
        'date': None,
        'image': None,
        'banner': False,
        'share': [],
        'share_heading': '',
        'url': _rel_url(page),
        'meta': [],
        'location': '',
        'audio': None,
        'action': None,
        'accent': 'red',
        # Follow the page's light/dark setting so the hero matches the body and
        # the header on a Dark landing (BugHerd #136).
        'surface': getattr(page, 'surface', 'light') or 'light',
    }


def podcast_series_hero_data(page, simple=False):
    """Series home BRANDED hero (frame 1360:113331): breadcrumb · title ·
    series description | vertical rule | series logo (image_logo, with the
    static Policy Prompt fallback for podcast series). The description is the
    series body's paragraph richtexts, unwrapped from the legacy
    paragraph-block chrome. Subscribe/Follow links live in the Latest Episode
    section's hero, not here."""
    page = page.specific
    data = _base(page, 'series', simple)
    data['logo'] = getattr(page, 'image_logo', None)
    # PP-logo fallback applies only to podcast series (has audio episodes) —
    # video series homes must not get podcast branding (Evan, 2026-07-03) —
    # and only to the Policy Prompt series itself: other podcast series brand
    # via image_logo or carry no brand (BugHerd #312/#314).
    from multimedia.models import MultimediaPage
    data['is_podcast'] = MultimediaPage.objects.live().filter(
        multimedia_series=page, multimedia_type='audio').exists()
    data['is_policy_prompt'] = page.slug == POLICY_PROMPT_SERIES_SLUG
    # Single HTML string — the split-hero partial takes one description value.
    data['description'] = ''.join(
        str(b.value) for b in (page.body or []) if b.block_type == 'paragraph'
    )
    return data


def video_hero_data(page, simple=False):
    """Video / Multimedia hero (content layout, no banner) — eyebrow pill · title ·
    excerpt · byline · date · share. The video player lives in the page body, not
    the hero."""
    page = page.specific
    data = _base(page, 'content', simple)
    data['banner'] = False
    return _apply_content_toggles(page, data)


def person_hero_data(page, simple=False):
    """Expert Bio hero — headshot beside eyebrow(programs) + name + role + bio.
    Reuses the expert_data superset (programs + share_links are hero-only)."""
    from core.cards import expert_data
    from core.templatetags.core_tags import formerize_position
    page = page.specific
    data = expert_data(page)
    data['layout'] = 'expert'
    data['simple'] = simple
    # The trail names the person's role listing (BugHerd #361; DPH cohort per
    # #342; Experts as the fallback per #208). Person pages sit directly under
    # Home, so the generic tree trail would only repeat the person's own name.
    data['breadcrumb'] = _person_role_crumbs(page) or _breadcrumb(page)
    if simple:
        data['bio'] = ''
    # expert_data.share_links is a {platform: url} dict; the share-buttons molecule
    # wants [{platform, url}]. Drop empties.
    data['share'] = [
        {'platform': platform, 'url': url}
        for platform, url in (data.get('share_links') or {}).items() if url
    ]
    # Archived profile: no bio, and the role reads as a former one (Jennifer,
    # BugHerd #478). The site already follows this rule everywhere else — the
    # page's own meta description (people/person_page.html) and the byline's
    # author block (includes/about_the_author.html) both swap the bio for
    # "Former <position>". The hero was the last place still showing the bio.
    if getattr(page, 'archive', 0):
        data['bio'] = ''
        if data.get('role'):
            data['role'] = formerize_position(data['role'])

    # Expert hero section toggles (HeroExpertTogglesAbstract).
    if not getattr(page, 'show_hero_breadcrumb', True):
        data['breadcrumb'] = []
    if not getattr(page, 'show_hero_role', True):
        data['role'] = ''
    if not getattr(page, 'show_hero_bio', True):
        data['bio'] = ''
    if not getattr(page, 'show_hero_expertise', True):
        data['expertise_tags'] = []
    if not getattr(page, 'show_hero_programs', True):
        data['programs'] = []
    if not getattr(page, 'show_hero_social', True):
        data['share'] = []
    return data


def job_posting_hero_data(page, simple=False):
    """Job posting hero — breadcrumb · title · short description · closing date.

    A posting has no byline, publishing date or type label, so it takes the
    listing hero's plain shape and adds the closing date and the share row
    (Kay + Tia, BugHerd #366: style postings like the other post types).
    """
    page = page.specific
    data = listing_hero_data(page, simple)
    data['excerpt'] = '' if simple else _plain(page.short_description)
    closing = page.closing_date_text
    data['meta'] = [closing] if closing else []
    data['share'] = _share_links(page)
    data['share_heading'] = 'Share'
    return data


# Page-model → presenter. ContentPage subclasses dispatch by class name; callers
# can also call a specific presenter directly.
def hero_data(page, simple=False, invite=None, variant=None):
    """Polymorphic dispatch to the right per-type hero presenter. ``invite``
    and ``variant`` are event-only (on-site registration action for private
    events; ``'registration'`` = the flow pages' dark hero)."""
    page = page.specific
    cls = page.__class__.__name__
    if cls == 'PersonPage':
        return person_hero_data(page, simple)
    if cls == 'PublicationPage':
        if getattr(getattr(page, 'publication_type', None), 'title', '') == 'Books':
            return publication_book_hero_data(page, simple)
        return publication_hero_data(page, simple)
    if cls == 'EventPage':
        return event_hero_data(page, simple, invite=invite, variant=variant)
    if cls == 'ThemePage':
        return theme_hero_data(page, simple)
    if cls == 'ProjectPage':
        return project_hero_data(page, simple)
    if cls == 'BasicPage':
        return basic_hero_data(page, simple)
    if cls == 'JobPostingPage':
        return job_posting_hero_data(page, simple)
    # Router landings compose from body modules; without an authored hero they
    # take the plain breadcrumb · title · subtitle hero (not the article hero
    # the fall-through would give them).
    if cls in ('EventListPage', 'PersonListPage', 'AnnualReportListPage',
               'ArticleLandingPage', 'SubscribePage'):
        return listing_hero_data(page, simple)
    if cls == 'MultimediaSeriesPage':
        return podcast_series_hero_data(page, simple)
    if cls == 'MultimediaPage':
        # Podcasts (audio) get the branded two-column hero; video/other gets the
        # plain no-banner content hero.
        if getattr(page, 'multimedia_type', '') == 'audio':
            return podcast_hero_data(page, simple)
        return video_hero_data(page, simple)
    return article_hero_data(page, simple)

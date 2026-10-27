"""Shared service for the placeable faceted-listing module (the "router as a
block").

The existing routers (`/events/`, `/experts/`, `/about/annual-report/`,
`/search/`) build their `router_*` context inside a page model's `get_context`.
This module generalises that so the *same* faceted listing can live inside a
StreamField block and run inside a composable tab panel — multiple instances on
one page, each owning a stable per-instance ``prefix`` so their query params
never collide (decision D2).

A block instance's value supplies the **card type**, the **scope** (program /
publication subtype / person type), which **facets** to show, and the
``prefix``. ``build_listing_context`` reads the request's ``<prefix>-*`` params,
runs the scoped/filtered query, paginates, and returns the shared ``router_*``
keys that ``includes/router_results_partial.html`` + ``router.js`` already
consume — plus a generic ``facets`` list the block template renders.

Card-type handlers each return ``(queryset, facets, selected, has_filters)``.
Add a new archive listing by adding a handler + a ``includes/router_items/``
template; the chrome, paging, AJAX dispatch and JS are shared.
"""

import logging

from django.core.paginator import Paginator
from django.db.models import F, Q
from django.db.models.functions import Lower

from core.routers import pager_range

logger = logging.getLogger(__name__)


PER_PAGE = 12

# Card types whose card is a full-width horizontal row (date · title · icon),
# laid out one-per-row rather than in the default 2-up grid
# (episode_row → All Episodes single column).
ROW_CARD_TYPES = {'episode_row'}

# Below this many (unfiltered) results a listing drops its facets — the filters
# cost more screen than they save (BugHerd #224).
FILTERS_MIN_RESULTS = 10

# The News archive TYPE set: these article types are
# surfaced ONLY on the CIGI News / CIGI in the News archives — their restricted
# TYPE facet shows exactly these three (design label → ArticleTypePage.slug) — and
# they are excluded from the general (/search/) and program resource hubs.
NEWS_TYPES = [
    ('news-release', 'CIGI News'),
    ('cigi-in-the-news', 'CIGI in the News'),
    ('op-eds', 'Opinion-Eds'),
]
NEWS_TYPE_SLUGS = [slug for slug, _ in NEWS_TYPES]

# The Opinions archive TYPE set (the legacy /opinions/ subtype filter):
# design label → ArticleTypePage.slug.
OPINION_TYPES = [
    ('opinion', 'Opinion'),
    ('op-eds', 'Op-Eds'),
    ('essays', 'Essays'),
    ('interviews', 'Interviews'),
]
OPINION_TYPE_SLUGS = [slug for slug, _ in OPINION_TYPES]

# Resource TYPE facet (design sidebar: TAGS + TYPE + YEAR, e.g. the expert
# single's More From This Expert — 1321:53357): content-type filter mapped to
# the concrete page models (labels match ContentPage.contenttype).
RESOURCE_TYPES = [
    ('opinion', 'Opinion', 'articlepage'),
    ('publication', 'Publication', 'publicationpage'),
    ('multimedia', 'Multimedia', 'multimediapage'),
    ('event', 'Event', 'eventpage'),
]
RESOURCE_TYPE_MODELS = {value: model for value, _, model in RESOURCE_TYPES}

# card_type → the per-item template under includes/router_items/.
ITEM_TEMPLATES = {
    'resource': 'includes/router_items/resource.html',
    'resource-visual': 'includes/router_items/resource_visual.html',
    'publication': 'includes/router_items/publication.html',
    'episode_row': 'includes/router_items/episode_row.html',
    'event': 'includes/router_items/event.html',
    'expert': 'includes/router_items/expert.html',
    'news': 'includes/router_items/news.html',
    'opinion': 'includes/router_items/news.html',  # same listing row as the news archives
    'person': 'includes/router_items/person.html',
    'report': 'includes/router_items/annual_report.html',
    'staff': 'includes/router_items/staff.html',
}

# Person-type scopes the block exposes (PersonType ids verified against the DB).
# A value may be a single id or a list of ids (e.g. Senior Management & Board).
PERSON_TYPE_IDS = {
    'expert': 4,
    'research_fellow': 14,
    'speaker': 15,
    'staff': 16,
    'dph_fellow': 17,
    'dph_speaker': 18,  # DPH Speaker (people 0057, BugHerd #177) — NOT the legacy event-speaker tag above
    'management_team': 7,
    'board': 1,
    'management_board': [7, 1],  # Senior Management & Board (Leadership page)
    # Expert roles (people 0063, BugHerd #359) — backfilled from position text.
    'research_director': 19,
    'distinguished_fellow': 20,
    'senior_fellow': 21,
    'fellow': 22,
}

# The /experts/ Type facet offers exactly these roles, in this order (Juode,
# BugHerd #359) — Staff/Management belong to the staff directory, not here.
EXPERT_ROLE_TYPE_IDS = [19, 20, 21, 22]
# Facet labels are plural (Tia, BugHerd #358: "Research Directors", "Senior
# Fellows" …). Display only — the PersonType names stay singular because they
# feed the person page's body classes and role checks.
EXPERT_ROLE_LABELS = {
    19: 'Research Directors',
    20: 'Distinguished Fellows',
    21: 'Senior Fellows',
    22: 'Fellows',
}


def _unaccent_name():
    """Order people A–Z by surname then forename, accent-insensitive (mirrors the
    built experts/staff routers)."""
    from django.contrib.postgres.lookups import Unaccent  # noqa: F401  (registers lookup)
    return (Unaccent(Lower('last_name')), Unaccent(Lower('first_name')))


def _topics_in(catalogue, relation='topics'):
    """The TOPIC facet's options, limited to topics the listing's catalogue
    actually carries. An option that can never match is a no-results trap
    (Tia, BugHerd #480 — "IP" on the ADT research tab returned nothing);
    the person facets already follow this rule. ``catalogue`` is the scoped
    queryset BEFORE user filters, so a picked topic never collapses the list.
    ``relation`` names the topic field — experts carry ``derived_topics``
    (BugHerd #521)."""
    from research.models import TopicPage
    ids = {i for i in catalogue.values_list('%s__id' % relation, flat=True) if i}
    return TopicPage.objects.live().filter(archive=0, id__in=ids).order_by('title')


# --- text search -------------------------------------------------------------
# Router search ran a literal `title__icontains`, so a query only matched the
# title. Searching a podcast brand returned the three episodes that happened to
# name it, not the series' sixty (Tim, BugHerd #497). Every router now queries
# the same Elasticsearch index the site-wide search uses, so body copy,
# subtitles and search terms count too.
#
# The index query runs on a live/public model queryset and nothing else. Wagtail
# turns a queryset's filters into index filters, and most of our scoping fields
# are not FilterFields — person_types raises outright. So the index matches and
# the database scopes: ids in, ORM narrows. That also leaves every handler's
# ordering, distinct(), specific() and prefetch chain untouched.
SEARCH_MATCH_CAP = 2000


def _search_ids(index_qs, q, cap=SEARCH_MATCH_CAP):
    """Ids of pages whose indexed content matches ``q``.

    Returns ``None`` when the index is unreachable, so the caller can fall back.

    Every term must match (``operator='and'``): with the default OR, a search
    for "policy prompt" listed every episode that mentioned "policy" anywhere,
    not the Policy Prompt series (Tim, BugHerd #506).
    """
    try:
        return [page.pk for page in index_qs.search(q, operator='and')[:cap]]
    except Exception:
        logger.exception('Router search fell back to title matching for %r', q)
        return None


def _apply_search(qs, index_qs, q, fallback):
    """Narrow ``qs`` to the pages matching ``q``.

    ``fallback`` is the Q object to use when the index is unavailable — the
    literal substring each handler used before, so a router keeps working when
    the cluster does not. A query matching more than ``SEARCH_MATCH_CAP`` pages
    keeps its most relevant matches; the listing then orders those by its own
    rule, as it always has.
    """
    if not q:
        return qs
    ids = _search_ids(index_qs, q)
    return qs.filter(fallback) if ids is None else qs.filter(pk__in=ids)


# --- per-card-type handlers --------------------------------------------------
# Each handler reads the prefixed params via the `P`/`PL` accessors and returns
# (queryset, facets, selected, has_filters). `facets` is a list of facet dicts
# the template renders generically:
#   {'key','label','open','options':[{'value','label','checked'}]}

def _resource_handler(P, PL, scope, enabled):
    """Program- or theme-scoped resource listing (Resource Hub tab). Scopes to a
    ``research.ProjectPage``'s content — or, on a theme page, to the content of
    the theme's programs (QA regroup 22:26). The instance's content-type toggles
    restrict the catalogue and drive the TYPE facet (QA regroup 17:46/18:08)."""
    from core.models import ContentPage
    from research.models import TopicPage

    program = scope.get('program')
    theme = scope.get('theme')
    author = scope.get('author')
    if program:
        base = program.content_pages.live().public()
    elif theme:
        program_ids = list(theme.theme_programs.values_list('program_id', flat=True))
        base = (ContentPage.objects.live().public().filter(projects__in=program_ids)
                if program_ids else ContentPage.objects.none())
    elif author is not None:
        # Person-scoped listing (the expert single's "From This Expert").
        # ``author_extra_ids`` = the profile's hand-curated
        # additional_authored_pages (kept from the legacy React table).
        cond = Q(authors__author=author)
        extra = scope.get('author_extra_ids') or []
        if extra:
            cond = cond | Q(id__in=extra)
        base = ContentPage.objects.live().public().filter(cond)
    elif scope.get('no_program'):
        # The Archive page: live content tagged to NO current-IA program
        # (Evan, 2026-09-10). News types stay in — they belong to no program
        # either, and this is the one listing meant to reach everything.
        from research.models import ThemeProgram
        current_ids = list(ThemeProgram.objects.values_list('program_id', flat=True))
        base = ContentPage.objects.live().public().exclude(projects__in=current_ids)
    else:
        base = ContentPage.objects.live().public()
    if not scope.get('no_program'):
        # News types (CIGI News / In the News / Op-Eds) live only on their own
        # archives — exclude them from the program resource hub.
        base = base.exclude(articlepage__article_type__slug__in=NEWS_TYPE_SLUGS)
    # The instance's content-type toggles restrict the whole catalogue; the
    # TYPE facet then offers only the enabled types (empty = all four).
    allowed = [t for t in (scope.get('content_types') or []) if t in RESOURCE_TYPE_MODELS]
    if allowed:
        base = base.filter(content_type__model__in=[RESOURCE_TYPE_MODELS[t] for t in allowed])
    base = base.order_by(F('publishing_date').desc(nulls_last=True))

    q = P('q')
    sel_topics = [t for t in PL('topic') if t.isdigit()]
    sel_types = [t for t in PL('type')
                 if t in RESOURCE_TYPE_MODELS and (not allowed or t in allowed)]
    sel_years = [y for y in PL('year') if y.isdigit() and 1000 <= int(y) <= 9999]

    qs = base
    qs = _apply_search(qs, ContentPage.objects.live().public(), q, Q(title__icontains=q))
    if sel_topics:
        qs = qs.filter(topics__id__in=sel_topics)
    if sel_types:
        qs = qs.filter(content_type__model__in=[RESOURCE_TYPE_MODELS[t] for t in sel_types])
    if sel_years:
        qs = qs.filter(publishing_date__year__in=[int(y) for y in sel_years])
    # .specific() for the card's type_of_content; prefetch the per-card topic
    # pills + author byline so a page of cards doesn't N+1 (mirrors the built
    # /experts/ router's prefetch pattern).
    qs = qs.distinct().specific().prefetch_related('topics__program_theme', 'authors__author')

    facets = []
    if 'topic' in enabled:
        topics = _topics_in(base)  # in-scope options only (BugHerd #480)
        facets.append({
            # The expert single's embed labels this group "Tags" (1321:53357).
            'key': 'topic', 'label': scope.get('topic_label') or 'Topic', 'open': True,
            'options': [{'value': t.id, 'label': t.title,
                         'checked': str(t.id) in sel_topics} for t in topics],
        })
    if 'type' in enabled:
        facets.append({
            'key': 'type', 'label': 'Type', 'open': False,
            'options': [{'value': v, 'label': label, 'checked': v in sel_types}
                        for v, label, _ in RESOURCE_TYPES
                        if not allowed or v in allowed],
        })
    if 'year' in enabled:
        years = [d.year for d in base.dates('publishing_date', 'year', order='DESC')]
        facets.append({
            'key': 'year', 'label': 'Year', 'open': False,
            'options': [{'value': y, 'label': y,
                         'checked': str(y) in sel_years} for y in years],
        })
    selected = {'q': q}
    return qs, facets, selected, bool(q or sel_topics or sel_types or sel_years)


def _publication_handler(P, PL, scope, enabled):
    """Publication-subtype listing (DPH Working Papers tab). Scopes to a
    PublicationTypePage (default Working Paper); facets = year."""
    from publications.models import PublicationPage, PublicationTypePage

    base = PublicationPage.objects.live().public()
    pub_type_id = scope.get('publication_type_id')
    if pub_type_id:
        base = base.filter(publication_type_id=pub_type_id)
    elif 'publication_type_id' in scope:
        # A subtype was configured but its slug didn't resolve (e.g. renamed) —
        # show nothing rather than silently leaking the whole publication catalogue.
        base = base.none()
    base = base.order_by(F('publishing_date').desc(nulls_last=True))

    q = P('q')
    sel_topics = [t for t in PL('topic') if t.isdigit()]
    sel_years = [y for y in PL('year') if y.isdigit() and 1000 <= int(y) <= 9999]

    qs = base
    qs = _apply_search(qs, PublicationPage.objects.live().public(), q, Q(title__icontains=q))
    if sel_topics:
        qs = qs.filter(topics__id__in=sel_topics)
    if sel_years:
        qs = qs.filter(publishing_date__year__in=[int(y) for y in sel_years])
    # Prefetch the per-card topic pills + author byline (PublicationPage is already
    # the specific type, so no .specific() needed) — avoids N+1 on a page of cards.
    qs = qs.distinct().prefetch_related('topics__program_theme', 'authors__author')

    facets = []
    # Topic, on the same terms as the resource/news/opinion/event listings
    # (BugHerd #442 — Juode: the Working Papers tab was missing it). Options are
    # the topics this subtype's catalogue carries, so none is a no-results trap.
    if 'topic' in enabled:
        topics = _topics_in(base)
        facets.append({
            'key': 'topic', 'label': 'Topic', 'open': True,
            'options': [{'value': t.id, 'label': t.title,
                         'checked': str(t.id) in sel_topics} for t in topics],
        })
    if 'year' in enabled:
        years = [d.year for d in base.dates('publishing_date', 'year', order='DESC')]
        facets.append({
            # Year leads only when it is the sole group, as it was before Topic.
            'key': 'year', 'label': 'Year', 'open': 'topic' not in enabled,
            'options': [{'value': y, 'label': y,
                         'checked': str(y) in sel_years} for y in years],
        })
    selected = {'q': q}
    return qs, facets, selected, bool(q or sel_topics or sel_years)


def _people_queryset(person_type_id):
    from people.models import PersonPage
    qs = PersonPage.objects.live().public().filter(archive=0)
    if not person_type_id:
        # No resolved person type → show nothing rather than every PersonPage on
        # the site (a person listing is always scoped to a type).
        return qs.none()
    # A scope may map to one id or several (e.g. Senior Management & Board).
    ids = person_type_id if isinstance(person_type_id, (list, tuple)) else [person_type_id]
    return qs.filter(person_types__id__in=ids).distinct().order_by(*_unaccent_name())


def _person_facets(qs, scope_ids, enabled, sel_types, sel_themes,
                   topic_label='Topic'):
    """Shared TYPE + TOPIC facets for the people handlers.

    TYPE lists the other roles the listed people hold — the type that scopes the
    listing is excluded, exactly as the expert handler drops "Expert" from its
    own list. TOPIC lists themes, reached through derived_topics: the expert
    listing's Theme (BugHerd #521). ``topic_label`` renames that facet where a
    listing calls it something else. (The DPH cohort page called it "Cohort"
    for BugHerd #365 until it gained real Type + Term facets — #365/#440.)
    """
    from people.models import PersonType
    from research.models import ThemePage

    ids = scope_ids if isinstance(scope_ids, (list, tuple)) else [scope_ids]
    facets = []
    if 'type' in enabled:
        # "Person" is the catch-all type — it says nothing about a role, so as a
        # filter option it is noise (Evan, BugHerd #231). One staff record holds
        # it today. Excluded by name: the type table is migration-managed, and
        # the name is the stable half of it.
        types = (PersonType.objects.filter(personpage__in=qs)
                 .exclude(name='Person')
                 .exclude(pk__in=[i for i in ids if i])
                 .distinct().order_by('name'))
        options = [{'value': t.id, 'label': t.name,
                    'checked': str(t.id) in sel_types} for t in types]
        # A one-option facet is noise — the same rule the resource TYPE facet uses.
        if len(options) > 1:
            facets.append({'key': 'type', 'label': 'Role', 'open': True,
                           'options': options})
    if 'topic' in enabled:
        # Only themes these people actually carry — an option that can never
        # match is worse than no option.
        theme_ids = {
            i for i in qs.values_list('derived_topics__program_theme__id', flat=True)
            if i
        }
        themes = (ThemePage.objects.live().filter(archive=0, id__in=theme_ids)
                  .order_by('path'))
        options = [{'value': t.id, 'label': t.title,
                    'checked': str(t.id) in sel_themes} for t in themes]
        if len(options) > 1:
            facets.append({'key': 'topic', 'label': topic_label, 'open': True,
                           'options': options})
    return facets


def _dph_fellow_facets(qs, enabled, sel_status, sel_themes, sel_terms):
    """TYPE · TOPIC · TERM for the DPH "Current Cohort and Alumni" listing, in
    the wireframe's order (BugHerd #365/#440).

    TYPE is Current Cohort / Alumni, read from each fellow's own status. It
    reuses the authored ``type`` key, so the block needs no new choice (a new
    choice would migrate every DS body); Role never built here anyway — fellows
    hold one other type. TERM is appended unconditionally, like the staff Last
    Name facet. Both list only values fellows actually carry, so until CIGI
    fills the data neither appears and the listing is unchanged.
    """
    from people.models import DPHTerm, PersonPage

    facets = []
    if 'type' in enabled:
        present = set(qs.order_by().values_list('dph_status', flat=True))
        statuses = [s for s in PersonPage.DPHStatus if s in present]
        # "All" plus one status is noise — both must exist.
        if len(statuses) > 1:
            options = [{'value': '', 'label': 'All', 'checked': not sel_status}]
            options += [{'value': s.value, 'label': s.label,
                         'checked': sel_status == s.value} for s in statuses]
            facets.append({'key': 'type', 'label': 'Type', 'open': True,
                           'single': True, 'options': options})
    facets += _person_facets(qs, PERSON_TYPE_IDS['dph_fellow'],
                             [f for f in enabled if f == 'topic'], [], sel_themes)
    # Newest first (model ordering); a term nobody carries is not offered.
    terms = DPHTerm.objects.filter(fellows__in=qs).distinct()
    options = [{'value': t.id, 'label': t.name,
                'checked': str(t.id) in sel_terms} for t in terms]
    if len(options) > 1:
        # Collapsed, as the wireframe draws it.
        facets.append({'key': 'term', 'label': 'Term', 'open': False,
                       'options': options})
    return facets


def _person_handler(P, PL, scope, enabled):
    """Person listing (DPH Cohort = DPH Fellow; DPH Speakers = Speaker).

    Facets: Role (the other person types these people hold) and Topic (themes,
    via derived_topics — 85% of DPH people carry them). Topic is the default when
    the author enabled nothing this card type can build (BugHerd #231). DPH
    fellows get Type (Current Cohort / Alumni), Topic and Term instead
    (BugHerd #365/#440, ``_dph_fellow_facets``).
    """
    person_type_id = scope.get('person_type_id')
    from people.models import PersonPage
    dph = person_type_id == PERSON_TYPE_IDS['dph_fellow']
    qs = _people_queryset(person_type_id)
    q = P('q')
    # For DPH fellows `type` carries a status, not a person-type id; anything
    # else (e.g. an old Role id) filters nothing.
    sel_types = [] if dph else [t for t in PL('type') if t.isdigit()]
    sel_status = P('type') if dph and P('type') in PersonPage.DPHStatus.values else ''
    sel_terms = [t for t in PL('term') if t.isdigit()] if dph else []
    sel_themes = [t for t in PL('topic') if t.isdigit()]
    qs = _apply_search(qs, PersonPage.objects.live().public(), q, Q(title__icontains=q))
    if sel_types:
        qs = qs.filter(person_types__id__in=sel_types)
    if sel_status:
        qs = qs.filter(dph_status=sel_status)
    if sel_terms:
        qs = qs.filter(dph_terms__id__in=sel_terms)
    if sel_themes:
        qs = qs.filter(derived_topics__program_theme__id__in=sel_themes)
    qs = qs.distinct().prefetch_related('person_types', 'derived_topics__program_theme')

    # The dispatcher already dropped unsupported groups; this is just the
    # default for an author who enabled nothing (BugHerd #231).
    enabled = list(enabled) or ['topic', 'type']
    if dph:
        facets = _dph_fellow_facets(
            _people_queryset(person_type_id), enabled, sel_status, sel_themes, sel_terms)
    else:
        facets = _person_facets(
            _people_queryset(person_type_id), person_type_id, enabled, sel_types,
            sel_themes)
    return qs, facets, {'q': q}, bool(q or sel_types or sel_status or sel_terms
                                       or sel_themes)


def _staff_handler(P, PL, scope, enabled):
    """Staff Directory (Leadership page), rendered as the staff card (name ·
    position · email · phone). Uses existing PersonPage fields — no new field.

    Facets: Last Name A–Z (single-select), reinstated for the staff directory
    (Juode, BugHerd #337); the initials offered are the ones staff actually
    carry. Topic, when the author enables it.

    No Role facet: it listed the other person types staff hold (Expert,
    Management Team …), which read as a random six-person subset to the
    directory's readers (Tim, BugHerd #360). Juode: the directory doesn't
    need it. It had been the #231 default when nothing was enabled; a
    Department facet is the intended replacement, but no department field
    or data exists yet, so that is new scope.
    """
    from people.models import PersonPage
    qs = _people_queryset(PERSON_TYPE_IDS['staff'])
    q = P('q')
    sel_types = []  # Role facet retired for staff (BugHerd #360); nothing to select
    sel_themes = [t for t in PL('topic') if t.isdigit()]
    qs = _apply_search(qs, PersonPage.objects.live().public(), q, Q(title__icontains=q))
    if sel_themes:
        qs = qs.filter(derived_topics__program_theme__id__in=sel_themes)
    # Last-name A–Z (BugHerd #337, Juode: the staff directory needs alphabetical
    # filtering by last name; single-select, always on for staff).
    sel_letter = P('letter').upper()[:1] if P('letter').isalpha() else ''
    if sel_letter:
        qs = qs.filter(last_name__istartswith=sel_letter)
    qs = qs.distinct().prefetch_related('person_types')

    enabled = [f for f in enabled if f != 'type']  # Role never builds here (#360)
    scope_qs = _people_queryset(PERSON_TYPE_IDS['staff'])
    facets = _person_facets(
        scope_qs, PERSON_TYPE_IDS['staff'], enabled, sel_types, sel_themes)
    letters = sorted({
        (name or '')[:1].upper() for name in scope_qs.values_list('last_name', flat=True)
        if (name or '')[:1].isalpha()})
    if letters:
        options = [{'value': '', 'label': 'All', 'checked': not sel_letter}]
        options += [{'value': l, 'label': l, 'checked': sel_letter == l} for l in letters]
        facets.append({'key': 'letter', 'label': 'Last Name', 'open': True,
                       'single': True, 'options': options})
    return qs, facets, {'q': q}, bool(q or sel_types or sel_themes or sel_letter)


def _expert_handler(P, PL, scope, enabled):
    """Expert listing (mirrors the built /experts/ router) — search · type ·
    theme · topic over live experts.

    The facet labelled Topic used to list the four research themes (John,
    BugHerd #521). Theme now lists them on ``<prefix>-theme``, and Topic lists
    the topics experts actually carry (derived_topics) on ``<prefix>-topic``,
    as every other listing does. Both ride on the authored ``topic`` choice,
    so the block needs no new choice (a new choice would migrate every DS body).
    """
    from people.models import PersonPage, PersonType
    from research.models import ThemePage

    q = P('q')
    sel_types = [t for t in PL('type') if t.isdigit()]
    sel_themes = [t for t in PL('theme') if t.isdigit()]
    sel_topics = [t for t in PL('topic') if t.isdigit()]
    if sel_topics:
        # Before #521 `<prefix>-topic` carried theme ids. Page ids are unique
        # across page types, so a theme id there is an old link: honour it as
        # the theme it named. The form re-posts it as `-theme` on the next change.
        legacy = set(ThemePage.objects.filter(id__in=sel_topics)
                     .values_list('id', flat=True))
        sel_themes += [t for t in sel_topics
                       if int(t) in legacy and t not in sel_themes]
        sel_topics = [t for t in sel_topics if int(t) not in legacy]

    base = PersonPage.objects.live().public().filter(person_types=4, archive=0)
    experts = base.order_by(*_unaccent_name())
    experts = _apply_search(experts, PersonPage.objects.live().public(), q, Q(title__icontains=q))
    if sel_types:
        experts = experts.filter(person_types__id__in=sel_types)
    if sel_themes:
        experts = experts.filter(derived_topics__program_theme__id__in=sel_themes)
    if sel_topics:
        # A separate filter() — a separate join — so Theme AND Topic may be
        # met by different topics on the same expert.
        experts = experts.filter(derived_topics__id__in=sel_topics)
    experts = experts.distinct().prefetch_related(
        'derived_topics__program_theme', 'content_pages_as_author__content_page')

    facets = []
    if 'type' in enabled:
        # Whitelist, not "every other type experts hold" — the old derivation
        # leaked Staff/Management Team into the expert filters (Tim + Juode,
        # BugHerd #359). Options follow EXPERT_ROLE_TYPE_IDS order, seniority
        # first, not A–Z.
        types = sorted(
            PersonType.objects.filter(pk__in=EXPERT_ROLE_TYPE_IDS),
            key=lambda t: EXPERT_ROLE_TYPE_IDS.index(t.pk))
        facets.append({
            'key': 'type', 'label': 'Type', 'open': True,
            'options': [{'value': t.id, 'label': EXPERT_ROLE_LABELS.get(t.pk, t.name),
                         'checked': str(t.id) in sel_types} for t in types],
        })
    if 'topic' in enabled:
        # Only themes and topics experts actually carry, and a one-option
        # facet is noise — the person facets' rules (BugHerd #521).
        theme_ids = {
            i for i in base.values_list('derived_topics__program_theme__id', flat=True)
            if i
        }
        themes = (ThemePage.objects.live().filter(archive=0, id__in=theme_ids)
                  .order_by('path'))
        options = [{'value': t.id, 'label': t.title,
                    'checked': str(t.id) in sel_themes} for t in themes]
        if len(options) > 1:
            facets.append({'key': 'theme', 'label': 'Theme', 'open': True,
                           'options': options})
        options = [{'value': t.id, 'label': t.title,
                    'checked': str(t.id) in sel_topics}
                   for t in _topics_in(base, 'derived_topics')]
        if len(options) > 1:
            facets.append({'key': 'topic', 'label': 'Topic', 'open': True,
                           'options': options})
    return experts, facets, {'q': q}, bool(q or sel_types or sel_themes or sel_topics)


def _news_handler(P, PL, scope, enabled):
    """CIGI News / CIGI in the News archive listing. These article types are surfaced ONLY on their own
    archives — the restricted TYPE facet shows exactly the three news types and
    nothing else; each archive lands prefiltered to its own type.

    Mapping (design label → real ``ArticleTypePage.slug``), corroborated by the
    existing hub exclusion in ``core/views.py``:
      CIGI News → news-release · CIGI in the News → cigi-in-the-news ·
      Opinion-Eds → op-eds. (Opinion / Essays / Interviews are NOT news types.)"""
    from articles.models import ArticlePage
    q = P('q')
    base = (ArticlePage.objects.live().public()
            .filter(article_type__slug__in=NEWS_TYPE_SLUGS)
            .order_by(F('publishing_date').desc(nulls_last=True)))

    # Prefilter: the archive lands with its own type already selected; an explicit
    # type selection overrides it, and Clear All (drops the param) returns to it.
    default = scope.get('news_prefilter')
    sel = [t for t in PL('type') if t in NEWS_TYPE_SLUGS]
    effective = sel or ([default] if default in NEWS_TYPE_SLUGS else [])

    sel_topics = [t for t in PL('topic') if t.isdigit()]
    sel_experts = [e for e in PL('experts') if e.isdigit()]
    sel_years = [y for y in PL('year') if y.isdigit() and 1000 <= int(y) <= 9999]

    qs = base
    if effective:
        qs = qs.filter(article_type__slug__in=effective)
    qs = _apply_search(qs, ArticlePage.objects.live().public(), q, Q(title__icontains=q))
    if sel_topics:
        qs = qs.filter(topics__id__in=sel_topics)
    if sel_experts:
        qs = qs.filter(authors__author__id__in=sel_experts)
    if sel_years:
        qs = qs.filter(publishing_date__year__in=[int(y) for y in sel_years])
    # Prefetch the row's topic pills + author byline (parity pass 2026-07-19:
    # the news row renders the full listing-card stack, not just pill + title).
    qs = qs.distinct().prefetch_related('topics__program_theme', 'authors__author')

    # Facet order per the listing rail (1689:101275): Topic · Type · Experts ·
    # Year — each honouring the block's authored facet set.
    facets = []
    if 'topic' in enabled:
        from research.models import TopicPage
        topics = _topics_in(base)  # in-scope options only (BugHerd #480)
        facets.append({
            'key': 'topic', 'label': 'Topic', 'open': True,
            'options': [{'value': t.id, 'label': t.title,
                         'checked': str(t.id) in sel_topics} for t in topics],
        })
    if 'type' in enabled:
        facets.append({
            'key': 'type', 'label': 'Type', 'open': False,
            'options': [{'value': slug, 'label': label, 'checked': slug in effective}
                        for slug, label in NEWS_TYPES],
        })
    if 'experts' in enabled:
        # Experts who authored content in the news archive (options list gets
        # the search-within-facet input via the >10 template rule).
        from people.models import PersonPage
        experts = (PersonPage.objects.live().public()
                   .filter(content_pages_as_author__content_page__in=base.values_list('id', flat=True))
                   .distinct().order_by(*_unaccent_name()))
        facets.append({
            'key': 'experts', 'label': 'Experts', 'open': False,
            'options': [{'value': p.id, 'label': p.title,
                         'checked': str(p.id) in sel_experts} for p in experts],
        })
    if 'year' in enabled:
        years = [d.year for d in base.dates('publishing_date', 'year', order='DESC')]
        facets.append({
            'key': 'year', 'label': 'Year', 'open': False,
            'options': [{'value': y, 'label': y,
                         'checked': str(y) in sel_years} for y in years],
        })
    return qs, facets, {'q': q}, bool(q or sel or sel_topics or sel_experts or sel_years)


def _opinion_handler(P, PL, scope, enabled):
    """Opinions archive listing (/opinions/, BugHerd — legacy ArticleLandingPage
    rebuild): the opinion-family article types with the restricted TYPE facet
    (Opinion / Op-Eds / Essays / Interviews). Same row template + facet shapes
    as the news archives.

    AUTHOR (single-select, BugHerd #432 — Jennifer: the Experts list names
    every opinion author, most of whom are not CIGI experts; Juode: tell CIGI
    Experts from Contributors): "CIGI Experts" keeps the opinions with at
    least one author of the Expert person type — the type the Experts router
    lists; former experts count (Evan) — "Contributors" the opinions whose
    authors are all other people. Opinions with no author sit in neither.
    """
    from articles.models import ArticlePage
    q = P('q')
    base = (ArticlePage.objects.live().public()
            .filter(article_type__slug__in=OPINION_TYPE_SLUGS)
            .order_by(F('publishing_date').desc(nulls_last=True)))

    sel = [t for t in PL('type') if t in OPINION_TYPE_SLUGS]
    sel_topics = [t for t in PL('topic') if t.isdigit()]
    sel_experts = [e for e in PL('experts') if e.isdigit()]
    sel_years = [y for y in PL('year') if y.isdigit() and 1000 <= int(y) <= 9999]
    sel_author = P('author') if P('author') in ('experts', 'contributors') else ''

    qs = base
    if sel_author == 'experts':
        qs = qs.filter(authors__author__person_types__id=PERSON_TYPE_IDS['expert'])
    elif sel_author == 'contributors':
        qs = (qs.filter(authors__isnull=False)
              .exclude(authors__author__person_types__id=PERSON_TYPE_IDS['expert']))
    if sel:
        qs = qs.filter(article_type__slug__in=sel)
    qs = _apply_search(qs, ArticlePage.objects.live().public(), q, Q(title__icontains=q))
    if sel_topics:
        qs = qs.filter(topics__id__in=sel_topics)
    if sel_experts:
        qs = qs.filter(authors__author__id__in=sel_experts)
    if sel_years:
        qs = qs.filter(publishing_date__year__in=[int(y) for y in sel_years])
    qs = qs.distinct().prefetch_related('topics__program_theme', 'authors__author')

    facets = []
    if 'topic' in enabled:
        from research.models import TopicPage
        topics = _topics_in(base)  # in-scope options only (BugHerd #480)
        facets.append({
            'key': 'topic', 'label': 'Topic', 'open': True,
            'options': [{'value': t.id, 'label': t.title,
                         'checked': str(t.id) in sel_topics} for t in topics],
        })
    if 'type' in enabled:
        facets.append({
            'key': 'type', 'label': 'Type', 'open': False,
            'options': [{'value': slug, 'label': label, 'checked': slug in sel}
                        for slug, label in OPINION_TYPES],
        })
    if 'author' in enabled:
        facets.append({
            'key': 'author', 'label': 'Author', 'open': True, 'single': True,
            'options': [
                {'value': '', 'label': 'All', 'checked': not sel_author},
                {'value': 'experts', 'label': 'CIGI Experts', 'checked': sel_author == 'experts'},
                {'value': 'contributors', 'label': 'Contributors', 'checked': sel_author == 'contributors'},
            ],
        })
    if 'experts' in enabled:
        from people.models import PersonPage
        experts = (PersonPage.objects.live().public()
                   .filter(content_pages_as_author__content_page__in=base.values_list('id', flat=True))
                   .distinct().order_by(*_unaccent_name()))
        facets.append({
            'key': 'experts', 'label': 'Experts', 'open': False,
            'options': [{'value': p.id, 'label': p.title,
                         'checked': str(p.id) in sel_experts} for p in experts],
        })
    if 'year' in enabled:
        years = [d.year for d in base.dates('publishing_date', 'year', order='DESC')]
        facets.append({
            'key': 'year', 'label': 'Year', 'open': False,
            'options': [{'value': y, 'label': y,
                         'checked': str(y) in sel_years} for y in years],
        })
    return qs, facets, {'q': q}, bool(q or sel or sel_topics or sel_author or sel_experts or sel_years)


def _episode_handler(P, PL, scope, enabled):
    """Podcast All-Episodes listing — audio multimedia, optional series scope.
    Optional single-select Season facet, scoped to the series' own seasons
    (SEASONS = Season N … + an "All" default)."""
    from multimedia.models import MultimediaPage
    q = P('q')
    base = MultimediaPage.objects.live().public().order_by(F('publishing_date').desc(nulls_last=True))
    series = scope.get('series')
    if series:
        # Scoped to a series → its episodes of whatever media type (Speaker
        # Series is video; podcast series are all audio, so no change there).
        base = base.filter(multimedia_series=series)
    else:
        # Unscoped generic all-episodes listing → podcast (audio) default.
        base = base.filter(multimedia_type='audio')

    sel_season = P('season')
    sel_years = [y for y in PL('year') if y.isdigit() and 1000 <= int(y) <= 9999]
    qs = base
    qs = _apply_search(qs, MultimediaPage.objects.live().public(), q, Q(title__icontains=q))
    if sel_season.isdigit():
        qs = qs.filter(podcast_season=int(sel_season))
    if sel_years:
        qs = qs.filter(publishing_date__year__in=[int(y) for y in sel_years])

    facets = []
    if 'season' in enabled:
        seasons = list(base.exclude(podcast_season__isnull=True)
                       .order_by('-podcast_season')
                       .values_list('podcast_season', flat=True).distinct())
        if seasons:
            # Checkbox-look list, "All" last (1312:29649).
            options = [{'value': s, 'label': 'Season %s' % s,
                        'checked': sel_season == str(s)} for s in seasons]
            options.append({'value': '', 'label': 'All', 'checked': not sel_season.isdigit()})
            facets.append({'key': 'season', 'label': 'Seasons', 'open': True,
                           'single': True, 'options': options})
    if 'year' in enabled:
        years = [d.year for d in base.dates('publishing_date', 'year', order='DESC')]
        facets.append({
            'key': 'year', 'label': 'Year', 'open': False,
            'options': [{'value': y, 'label': y,
                         'checked': str(y) in sel_years} for y in years],
        })
    return qs, facets, {'q': q}, bool(q or sel_season.isdigit() or sel_years)


def _event_handler(P, PL, scope, enabled):
    """Events listing (mirrors the retired /events/ page router) — search ·
    topic · type · location · date over live events. Browse order per the
    Events listing design: upcoming events soonest first, then past events most
    recent first (past rows render the compact card variant)."""
    from django.db.models import Case, When
    from django.utils import timezone
    from events.models import EventPage
    from research.models import TopicPage

    q = P('q')
    sel_topics = [t for t in PL('topic') if t.isdigit()]
    sel_types = PL('type')
    sel_locations = PL('location')
    year = P('year')
    month = P('month')
    day = P('day')

    now = timezone.now()
    events = EventPage.objects.live().public().annotate(
        is_past=Case(When(publishing_date__gte=now, then=0), default=1),
        upcoming_order=Case(When(publishing_date__gte=now, then=F('publishing_date'))),
    ).order_by('is_past', F('upcoming_order').asc(nulls_last=True), '-publishing_date')
    events = _apply_search(events, EventPage.objects.live().public(), q,
                           Q(title__icontains=q) | Q(short_description__icontains=q))
    if sel_topics:
        events = events.filter(topics__id__in=sel_topics)
    if sel_types:
        events = events.filter(event_type__in=sel_types)
    if sel_locations:
        events = events.filter(location_name__in=sel_locations)
    if year.isdigit() and 1000 <= int(year) <= 9999:
        events = events.filter(publishing_date__year=int(year))
    if month.isdigit():
        events = events.filter(publishing_date__month=int(month))
    if day.isdigit() and 1 <= int(day) <= 31:
        # Day-level filter from the sidebar calendar (1253:39873); only
        # meaningful with a month (+ year), which the calendar always sends.
        events = events.filter(publishing_date__day=int(day))
    events = events.distinct().prefetch_related('topics')

    facets = []
    if 'topic' in enabled:
        topics = _topics_in(EventPage.objects.live().public())  # in-scope options only (BugHerd #480)
        facets.append({
            'key': 'topic', 'label': 'Topic', 'open': True,
            'options': [{'value': t.id, 'label': t.title,
                         'checked': str(t.id) in sel_topics} for t in topics],
        })
    if 'location' in enabled:
        locations = (EventPage.objects.live().public()
                     .exclude(location_name='').exclude(location_name__isnull=True)
                     .values_list('location_name', flat=True).distinct().order_by('location_name'))
        facets.append({
            'key': 'location', 'label': 'Location',
            'options': [{'value': loc, 'label': loc,
                         'checked': loc in sel_locations} for loc in locations],
        })
    if 'type' in enabled:
        facets.append({
            'key': 'type', 'label': 'Event Type',
            'options': [{'value': v, 'label': lbl,
                         'checked': v in sel_types} for v, lbl in EventPage.EventTypes.choices],
        })
    if 'date' in enabled:
        # Calendar facet (1253:39873): Month/Year selects + JS month grid via
        # router-calendar.js; the block template renders it from `kind`.
        years = [d.year for d in (EventPage.objects.live().public()
                 .exclude(publishing_date__isnull=True)
                 .dates('publishing_date', 'year', order='DESC'))]
        facets.append({
            'key': 'date', 'label': 'Date', 'kind': 'calendar', 'open': True,
            'years': years,
            'selected_year': year, 'selected_month': month, 'selected_day': day,
        })
    has = bool(q or sel_topics or sel_types or sel_locations or year or month or day)
    return events, facets, {'q': q}, has


def _report_handler(P, PL, scope, enabled):
    """Annual-report listing (mirrors the retired /about/annual-report/ page
    router) — search · year over live reports, newest first."""
    from annual_reports.models import AnnualReportPage
    q = P('q')
    sel_years = [y for y in PL('year') if y.isdigit()]
    qs = AnnualReportPage.objects.live().public().order_by('-year')
    qs = _apply_search(qs, AnnualReportPage.objects.live().public(), q, Q(title__icontains=q))
    if sel_years:
        qs = qs.filter(year__in=sel_years)
    facets = []
    if 'year' in enabled:
        years = (AnnualReportPage.objects.live().public()
                 .values_list('year', flat=True).distinct().order_by('-year'))
        facets.append({
            'key': 'year', 'label': 'Year', 'open': True,
            'options': [{'value': y, 'label': y,
                         'checked': str(y) in sel_years} for y in years],
        })
    return qs, facets, {'q': q}, bool(q or sel_years)


# The facet groups each card type can actually BUILD (BugHerd #442). One source
# of truth: build_listing_context intersects the authored `facets` list with it,
# and the block's editor adapter narrows the picker to the same set — the admin
# used to offer all seven groups for every card type, so content entry ticked
# Topic + Type on a publication listing and the page rendered a bare search box.
# 'letter' is absent by design: the staff directory appends it unconditionally,
# so it is not an authored choice. So is 'term': the DPH fellow listing appends
# it the same way (BugHerd #365/#440). So is 'theme': the expert listing builds
# it beside Topic from the authored 'topic' choice (BugHerd #521).
FACETS_BY_CARD_TYPE = {
    'resource': ('topic', 'type', 'year'),
    'resource-visual': ('topic', 'type', 'year'),
    'publication': ('topic', 'year'),
    'person': ('type', 'topic'),
    'staff': ('topic',),  # no Role for the staff directory (BugHerd #360)
    'expert': ('type', 'topic'),
    'news': ('topic', 'type', 'experts', 'year'),
    'opinion': ('topic', 'type', 'author', 'experts', 'year'),
    'episode_row': ('season', 'year'),
    'event': ('topic', 'location', 'type', 'date'),
    'report': ('year',),
}

HANDLERS = {
    'resource': _resource_handler,
    'resource-visual': _resource_handler,
    'publication': _publication_handler,
    'person': _person_handler,
    'staff': _staff_handler,
    'expert': _expert_handler,
    'news': _news_handler,
    'opinion': _opinion_handler,
    'episode_row': _episode_handler,
    'event': _event_handler,
    'report': _report_handler,
}


def resolve_scope(value, page):
    """Turn a faceted-listing block value into a scope dict the handlers read.
    Resolves the program (auto picks up a ProjectPage placement), the publication
    subtype, the person type, and the multimedia series."""
    from streams.blocks import resolve_program

    card_type = value.get('card_type')
    scope = {}
    if value.get('author') is not None:
        # Synthetic page-level listing (expert single) — not block-authorable.
        scope['author'] = value['author']
        scope['author_extra_ids'] = value.get('author_extra_ids') or []
        if value.get('topic_label'):
            scope['topic_label'] = value['topic_label']
    elif card_type in ('resource', 'resource-visual'):
        scope['program'] = resolve_program(
            value.get('program_source'), value.get('program'), page)
        # Archive scope (Evan, 2026-09-10): content carrying no current-IA
        # program. Current-IA = theme-mapped, the same set the program routers
        # and the pills use — legacy-only tags count as "no program".
        if value.get('program_source') == 'none':
            scope['program'] = None
            scope['no_program'] = True
        # Theme auto-scope (QA regroup 22:26): an auto resource listing on a
        # theme page surfaces the content of the theme's programs.
        if scope['program'] is None and (value.get('program_source') or 'auto') == 'auto':
            from research.models import ThemePage
            specific = page.specific if page else None
            if isinstance(specific, ThemePage):
                scope['theme'] = specific
        # Per-instance content-type toggles (QA regroup 17:46).
        scope['content_types'] = [
            t for t in (value.get('content_types') or []) if t in RESOURCE_TYPE_MODELS]
    if card_type == 'publication':
        from publications.models import PublicationTypePage
        slug = value.get('publication_type') or 'working-paper'
        pt = PublicationTypePage.objects.filter(slug=slug).first()
        scope['publication_type_id'] = pt.id if pt else None
    if card_type in ('person',):
        scope['person_type_id'] = PERSON_TYPE_IDS.get(value.get('person_type') or 'dph_fellow')
    if card_type == 'news':
        scope['news_prefilter'] = value.get('news_prefilter') or None
    if card_type == 'episode_row':
        from multimedia.models import MultimediaSeriesPage
        if (value.get('series_source') or 'auto') == 'manual':
            chooser = value.get('series')
            scope['series'] = chooser.specific if chooser else None
        else:
            # Auto: the podcast series page this listing is placed on.
            specific = page.specific if page else None
            scope['series'] = specific if isinstance(specific, MultimediaSeriesPage) else None
    return scope


def listing_querystring(request, prefix):
    """The querystring the pager appends ``<prefix>-page`` to: every current GET
    param except this router's page cursor + the AJAX ``router`` signal. Preserves
    sibling routers' params and ``tab`` so paging one listing keeps the rest."""
    params = request.GET.copy()
    params.pop('%s-page' % prefix, None)
    params.pop('router', None)
    return params.urlencode()


def listing_clear_url(request, prefix):
    """Clear-all href for one listing: drop only this prefix's params (keep
    ``tab`` + sibling routers)."""
    params = request.GET.copy()
    for key in list(params.keys()):
        if key == ('%s-page' % prefix) or key.startswith('%s-' % prefix) or key == 'router':
            params.pop(key, None)
    qs = params.urlencode()
    return '%s?%s' % (request.path, qs) if qs else request.path


def default_listing_prefix(value):
    """Stable fallback prefix for a listing whose author left ``prefix`` blank.

    Blank prefixes used to collapse onto a single 'r', so with several listings
    on one page every AJAX fetch (lazy tab loads, filter swaps) matched the
    FIRST block and each tab rendered the first tab's results (BugHerd #180).
    Derived from the block's scope config, the fallback is identical on the
    page render and on the RouterServeMixin dispatch, and distinct wherever
    the listings actually differ. An authored prefix always wins.
    """
    import hashlib
    key = '|'.join(str(value.get(k) or '') for k in (
        'card_type', 'person_type', 'publication_type', 'news_prefilter',
        'content_types', 'heading'))
    return 'r' + hashlib.md5(key.encode()).hexdigest()[:6]


def build_listing_context(request, value, page=None, lazy=False, tab_slug=None):
    """Build the shared ``router_*`` context for one faceted-listing block value.

    ``lazy=True`` (an inactive tab panel — decision D3) renders the filter chrome
    (search + facet options, which are light queries) but defers the *heavy*
    paginated results query: the results region renders a placeholder marked
    ``data-router-lazy`` and ``tabs.js`` fetches the real results on first
    activation. The active tab (or a listing placed directly on a page body)
    renders fully.
    """
    prefix = value.get('prefix') or default_listing_prefix(value)
    card_type = value.get('card_type') or 'resource'
    show_filters = value.get('show_filters', True)
    # Drop any authored facet this card type cannot build (BugHerd #442) —
    # silently, because the picker no longer offers them and old values persist.
    enabled = [f for f in (value.get('facets') or [])
               if f in FACETS_BY_CARD_TYPE.get(card_type, ())]
    if card_type in ('resource', 'resource-visual'):
        # Resource listings auto-build their filters from the enabled content
        # types (QA regroup 18:08) — the authored facet list is ignored. One
        # enabled type drops the TYPE facet (a one-option facet is noise).
        allowed = [t for t in (value.get('content_types') or []) if t in RESOURCE_TYPE_MODELS]
        enabled = ['topic', 'year'] if len(allowed) == 1 else ['topic', 'type', 'year']
    show_search = value.get('show_search', True)
    per_page = value.get('per_page') or PER_PAGE

    def P(name):
        return (request.GET.get('%s-%s' % (prefix, name)) or '').strip()

    def PL(name):
        return request.GET.getlist('%s-%s' % (prefix, name))

    scope = resolve_scope(value, page)
    handler = HANDLERS.get(card_type, _resource_handler)
    qs, facets, selected, has_filters = handler(P, PL, scope, enabled)

    # Few results → no filters (BugHerd #224): a short list doesn't need facets.
    # Only when nothing is applied — an over-filtered result keeps its filters so
    # the reader can clear them. Counted here (a cheap COUNT) rather than off the
    # paginator, so a lazy tab panel agrees with its own results.
    if show_filters and not has_filters and qs.count() < FILTERS_MIN_RESULTS:
        show_filters = False

    base = {
        'router_prefix': prefix,
        'router_card_type': card_type,
        'router_show_filters': bool(show_filters),
        'router_show_search': bool(show_search),
        'router_results_template': ITEM_TEMPLATES.get(card_type, ITEM_TEMPLATES['resource']),
        'router_grid_modifier': (
            'ds-router__grid--rows' if card_type in ROW_CARD_TYPES
            # No-filter person grids (DPH Speakers) are 3-up (1595:82296).
            else 'ds-router__grid--three' if card_type == 'person' and not show_filters
            # Bordered report cards in a plain gap grid — no row/column rules
            # (Module Library annual-report frame).
            else 'ds-router__grid--plain' if card_type == 'report'
            else ''),
        'router_page_param': '%s-page' % prefix,
        'router_heading': value.get('heading'),
        'router_intro': value.get('intro'),
        'router_empty': value.get('empty_text') or 'No results match your filters.',
        'router_clear_url': listing_clear_url(request, prefix),
        'router_querystring': listing_querystring(request, prefix),
        'router_facets': facets if show_filters else [],
        'router_search_value': selected.get('q', ''),
        'router_has_filters': has_filters,
        'router_lazy': bool(lazy),
        # The owning tab's slug (no-JS hidden field). Prefer the slug threaded by
        # the Tabs template (correct even for inactive/lazy panels); fall back to
        # the request URL for a listing placed directly on a page body.
        'router_tab': tab_slug or request.GET.get('tab', ''),
    }
    # An empty SOURCE hides the whole module (BugHerd #297). Only a
    # visitor-filtered empty result keeps the no-results + clear-filters state.
    base['router_empty_source'] = not has_filters and not qs.exists()
    if lazy:
        return base

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('%s-page' % prefix))
    base.update({
        'router_results': page_obj.object_list,
        'router_page': page_obj,
        'router_total': paginator.count,
        'router_range_start': page_obj.start_index(),
        'router_range_end': page_obj.end_index(),
        'router_page_range': pager_range(page_obj),
    })
    return base


def find_faceted_listing_value(page, prefix):
    """Walk a page's ``body`` StreamField for the faceted-listing block whose
    ``prefix`` matches — top-level or nested in a composable Tabs block's panels.
    Used by ``RouterServeMixin`` to dispatch an AJAX ``router=<prefix>`` request to
    the right block (decision D4)."""
    body = getattr(page, 'body', None)
    if body is None:
        return None

    def scan(stream_value):
        for child in stream_value:
            if child.block_type == 'faceted_listing':
                # Normalise exactly like build_listing_context: a blank
                # authored prefix takes the same config-derived default, so
                # the AJAX lookup lands on the SAME block the page rendered
                # (BugHerd #180 — the old shared 'r' default made every tab
                # fetch the first listing's results).
                if (child.value.get('prefix') or default_listing_prefix(child.value)) == prefix:
                    return child.value
            elif child.block_type == 'composable_tabs':
                for tab in child.value.get('tabs') or []:
                    found = scan(tab.get('content'))
                    if found is not None:
                        return found
        return None

    return scan(body)

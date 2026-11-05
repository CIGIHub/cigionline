import base64
import io
from datetime import datetime
from pathlib import Path
from django import template
from django.template.defaultfilters import stringfilter
from django.urls import reverse
from wagtail.models import Site

register = template.Library()


@register.simple_tag(takes_context=True)
def breadcrumbs(context, page):
    """Build frontend breadcrumbs for a page, scoped to the current Site root.

    Returns a list of {title, url, current} dicts: linked ancestors from the
    site root (labelled "Home") down, then the current page (no link). Shared
    by hero templates so breadcrumbs stay consistent. See includes/alt_hero.html.
    """
    request = context.get('request')
    site = Site.find_for_request(request) if request else None
    root = site.root_page if site else None

    ancestors = page.get_ancestors().live()
    if root:
        # Trim to the current site's root and below (microsite-aware).
        ancestors = ancestors.descendant_of(root, inclusive=True)
    else:
        ancestors = ancestors.filter(depth__gt=1)  # drop the Wagtail root

    crumbs = []
    for ancestor in ancestors:
        is_root = root is not None and ancestor.pk == root.pk
        crumbs.append({
            'title': 'Home' if is_root else ancestor.title,
            # get_url(request) → relative path on the current site; the bare .url
            # property falls back to the Site's absolute root_url off-prod.
            'url': ancestor.get_url(request=request),
            'current': False,
        })
    crumbs.append({'title': page.title, 'url': None, 'current': True})
    return crumbs


@register.simple_tag(takes_context=True)
def document_qr(context, document):
    """
    Returns a dict with 'qr_image_data' (base64 PNG data URI) and 'scan_count'
    for the given Wagtail Document, encoding the /qr/doc/<id>/ redirect URL.
    Usage: {% document_qr document as qr %}
    """
    if not document or not document.pk:
        return {'qr_image_data': None, 'scan_count': 0}

    request = context.get('request')
    try:
        path = reverse('qr_document_redirect', args=[document.pk])
        redirect_url = request.build_absolute_uri(path) if request else path
    except Exception:
        redirect_url = None

    qr_image_data = None
    if redirect_url:
        try:
            import qrcode
            qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=6,
                border=4,
            )
            qr.add_data(redirect_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            encoded = base64.b64encode(buf.getvalue()).decode('ascii')
            qr_image_data = f'data:image/png;base64,{encoded}'
        except ImportError:
            pass

    try:
        from core.models import QRCodeDocumentScan
        scan_count = QRCodeDocumentScan.objects.get(document_id=document.pk).scan_count
    except Exception:
        scan_count = 0

    return {'qr_image_data': qr_image_data, 'scan_count': scan_count}


@register.filter
def no_protocol(value):
    return value.replace('http://', '').replace('https://', '')


@register.filter
def page_type(page):
    if page and hasattr(page, '_meta'):
        return page._meta.verbose_name.lower().replace(' ', '-')
    return ''


@register.filter
def in_list(value, the_list):
    return value in the_list.split(',')


@register.filter
def any_in_list(values, the_list):
    for value in values:
        if str(value) in the_list.split(','):
            return True
    return False


@register.filter
def renderable_people(items):
    """Filter an aside person-group list down to the rows its template would
    actually render (mirrors reading_author_group.html): authorship rows /
    chooser blocks / person pages whose person is present and not archived,
    plus plain-string guest blocks. Lets reading_body.html decide the whole
    rail on renderability — a group of only-archived people otherwise renders
    an empty ruled heading."""
    out = []
    for item in items or []:
        person = None
        block_type = getattr(item, 'block_type', None)
        if getattr(item, 'author', None):
            person = item.author
        elif getattr(item, 'editor', None):
            person = item.editor
        elif block_type == 'guest':
            if item.value:
                out.append(item)  # plain-string guest — name-only row
            continue
        elif block_type == 'guest_page':
            page = item.value.get('guest_page')
            person = page.specific if page else None
            if person is None or getattr(person, 'archive', False):
                # No page (or archived) — renders from the block's own fields
                # when a name is authored.
                if item.value.get('guest'):
                    out.append(item)
                continue
        elif getattr(item, 'value', None):
            person = getattr(item.value, 'specific', None)
        elif hasattr(item, 'specific'):
            person = item.specific
        if person is not None and not getattr(person, 'archive', False):
            out.append(item)
    return out


# A long aside group shows its first rows and folds the rest behind a
# "Show N more" toggle (Robert, BugHerd #523 revision, 20 Oct).
ASIDE_GROUP_COLLAPSE_AT = 5
ASIDE_GROUP_VISIBLE = 3


@register.filter
def split_aside_rows(items):
    """Split an aside person group into {'shown': [...], 'more': [...]}.

    Counts only rows that render (renderable_people — archived people drop
    out), so a group padded by archived people doesn't get a toggle it can't
    fill. Groups of ASIDE_GROUP_COLLAPSE_AT or more keep the first
    ASIDE_GROUP_VISIBLE rows in `shown`; shorter groups put every row there
    and leave `more` empty."""
    rows = renderable_people(items)
    if len(rows) >= ASIDE_GROUP_COLLAPSE_AT:
        return {'shown': rows[:ASIDE_GROUP_VISIBLE], 'more': rows[ASIDE_GROUP_VISIBLE:]}
    return {'shown': rows, 'more': []}


@register.filter
def promote_section_labels(html):
    """Podcast prose: promote short label paragraphs ("Credits:", "Further
    Reading:") to <h3> section headings so they take the brand heading
    treatment — the authored episode bodies carry them as plain <p>, and the
    design (Podcast Template) shows them as headings. A clear candidate is a
    paragraph whose entire text is ≤40 chars and ends with ':' (the colon is
    dropped). Everything else passes through untouched."""
    import re
    from django.utils.safestring import mark_safe

    def repl(match):
        text = re.sub(r'<[^>]+>', '', match.group(1))
        text = text.replace('\xa0', ' ').replace('&nbsp;', ' ').strip()
        if 0 < len(text) <= 40 and text.endswith(':'):
            return f'<h3>{text[:-1].strip()}</h3>'
        return match.group(0)

    return mark_safe(re.sub(r'<p[^>]*>(.*?)</p>', repl, str(html), flags=re.S))


@register.filter
def links_new_tab(html):
    """Open absolute http(s) links in a new tab — the footer address's map link
    (Tia, BugHerd #238). The address is authored rich text
    (core.FooterSettings.address) and Wagtail's editor exposes no target option
    for an external link, so the attribute is added at render time.

    Only absolute http(s) anchors are touched. Internal links, mailto:/tel:, and
    anchors that already carry a target pass through untouched. `rel` is only
    added where the anchor has none, so an authored rel survives."""
    import re
    from django.utils.safestring import mark_safe

    def repl(match):
        tag = match.group(0)
        if 'target=' in tag:
            return tag
        extra = ' target="_blank"' + ('' if 'rel=' in tag else ' rel="noopener"')
        return tag[:-1] + extra + '>'

    return mark_safe(re.sub(r'<a\s[^>]*href="https?://[^"]*"[^>]*>', repl, str(html)))


@register.filter
def unwrap_paragraphs(html):
    """Strip the <p> wrapper a rich-text field puts around its content, keeping
    the inline markup (bold/italic/link). For rich text rendered INSIDE another
    element — the collapsible paragraph's title sits in its h2/h3/h4, where the
    wrapper <p> is invalid HTML and the prose p styles overrode the heading
    look, so H2/H3/H4 all rendered as body text (Tim + Tia, BugHerd #471)."""
    import re
    from django.utils.safestring import mark_safe
    return mark_safe(re.sub(r'</?p[^>]*>', '', str(html)).strip())


@register.filter
def external_links_new_tab(html):
    """Open EXTERNAL absolute links in a new tab (Tia, BugHerd #464) — the
    reading body's migrated content is full of citation links, and the editor
    stores them without a target. Unlike links_new_tab (the footer's #238
    filter), absolute links back into cigionline.org stay in-tab: they are
    internal content that happens to be authored absolute. mailto:/tel:,
    relative links, and anchors with an authored target pass untouched."""
    import re
    from django.utils.safestring import mark_safe

    def repl(match):
        tag = match.group(0)
        href = match.group(1)
        if 'target=' in tag or re.match(r'https?://([^/"]*\.)?cigionline\.org', href):
            return tag
        extra = ' target="_blank"' + ('' if 'rel=' in tag else ' rel="noopener"')
        return tag[:-1] + extra + '>'

    return mark_safe(re.sub(r'<a\s[^>]*href="(https?://[^"]*)"[^>]*>', repl, str(html)))


@register.simple_tag(takes_context=True)
def include_with_self(context, template_name, self_value, **extra):
    """Render a block template outside a StreamField: Django's ``{% include %}``
    / ``{% with %}`` can't bind the name ``self`` (it collides with
    ``Context.push(**kwargs)``'s own ``self`` argument), so module templates
    that read ``self.*`` are re-rendered here with an explicit context dict —
    e.g. the expert single reusing the news-carousel/bento/experts-carousel
    modules data-driven."""
    from django.template.loader import render_to_string
    from django.utils.safestring import mark_safe

    ctx = context.flatten()
    ctx['self'] = self_value
    ctx.update(extra)
    return mark_safe(render_to_string(template_name, ctx, request=context.get('request')))


@register.simple_tag
def define(value):
    return value


@register.simple_tag
def titled_embed(url, title):
    """Wagtail ``{% embed %}`` plus an injected iframe ``title`` when the
    provider omits one (WCAG 4.1.2 — the Issuu document reader; see
    docs/redesign/wcag-audit.md). The title is the page title — no provider
    parsing or backfill."""
    from django.utils.html import format_html
    from django.utils.safestring import mark_safe
    from wagtail.embeds.embeds import get_embed
    from wagtail.embeds.exceptions import EmbedException

    try:
        html = get_embed(url).html
    except EmbedException:
        return ''
    if '<iframe' in html and 'title=' not in html:
        html = html.replace('<iframe', format_html('<iframe title="{}"', title), 1)
    return mark_safe(html)


@register.filter
def social_string(value):
    return value.replace(' ', '+')


@register.filter
def file_extension(value):
    return Path(value).suffix


@register.simple_tag(takes_context=True)
def preview_cache_bust(context):
    if context['request']:
        if hasattr(context['request'], 'is_preview'):
            if context['request'].is_preview:
                return datetime.now().strftime("%Y%m%d%H%M%S")
    return ''


@register.filter
@stringfilter
def formerize_position(value):
    if 'former' not in value.lower():
        cigi_prefix = 'CIGI ' if 'cigi' not in value.lower() else ''
        return f'Former {cigi_prefix}{value}'
    return value


@register.filter
@stringfilter
def trim_trailing_slash(value):
    if value.endswith('/'):
        return value[:-1]
    return value


@register.filter
@stringfilter
def dash_case(value):
    return value.lower().replace(' ', '-')


@register.filter(name='split_to_spans')
def split_to_spans(value):
    if not isinstance(value, str):
        return value
    return ''.join(f'<span id="char-{i}">{char}</span>' for i, char in enumerate(value))


@register.filter
@stringfilter
def revert_snake_case(value):
    return value.lower().replace('_', ' ')


@register.filter
def remove_trailing_s(value):
    if isinstance(value, str) and value.endswith('s'):
        return value[:-1]
    return value

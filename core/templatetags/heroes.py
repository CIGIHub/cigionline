from django import template

from core.heroes import hero_data

register = template.Library()


@register.inclusion_tag('includes/heroes/hero.html', takes_context=True)
def page_hero(context, page, simple=False, invite=None, embedded=False,
              title=None, variant=None):
    """Render the CPT hero for a page.

    Usage: ``{% page_hero self %}``. ``core.heroes.hero_data`` dispatches to the
    per-type presenter (article/opinion/news, publication, event, expert,
    podcast); ``includes/heroes/hero.html`` selects the matching layout. Pass
    ``simple=True`` for the compact variant. ``invite`` is event-only: the
    invite from EventPage.serve, so private events surface the on-site
    Register action with the token. ``variant`` is event-only too:
    ``'registration'`` renders the dark hero of the on-site registration pages
    (Event Form 1705:20340). ``embedded=True`` renders the hero as a
    page SECTION rather than page chrome — no breadcrumb trail and no series
    logo (incl. the PP fallback) — e.g. the series home's "Latest Episode"
    embed (frame 1312:31660).
    """
    data = hero_data(page, simple=simple, invite=invite, variant=variant)
    if title is not None:
        # Heading override for serve()-rendered states whose heading is not
        # the page title (e.g. the subscribe landing's thank-you, #265).
        data['title'] = title
        data['excerpt'] = ''
    if embedded:
        data['breadcrumb'] = []
        data['logo'] = None
        data['is_policy_prompt'] = False  # gates the template's PP-logo fallback
    return {
        'hero': data,
        # Page-level accent scheme (e.g. DPH green) — hero templates fall back
        # to it where the presenter sets no accent.
        'main_accent_scheme': context.get('main_accent_scheme'),
    }

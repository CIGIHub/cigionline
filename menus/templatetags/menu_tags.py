from django import template

from ..models import Menu

register = template.Library()


@register.simple_tag()
def get_menu_items(slug):
    return Menu.objects.prefetch_related(
        'menu_items__link_page',
        'menu_items__submenu__menu_items__link_page',
    ).get(slug=slug).menu_items.all()


@register.simple_tag()
def get_menu(slug):
    """
    Return the Menu with this slug (items + link pages prefetched), or None if
    it doesn't exist. Lets templates render menu-driven chrome (e.g. the footer)
    that degrades gracefully before an editor has created the menu.
    """
    return Menu.objects.prefetch_related(
        'menu_items__link_page',
        'menu_items__submenu__menu_items__link_page',
        'menu_items__submenu__bottom_link_page',  # header dropdown foot (BugHerd #539)
    ).filter(slug=slug).first()


@register.simple_tag(takes_context=True)
def nav_is_active(context, item):
    """
    True when the request path lives under this menu item's link target (exact
    match for the homepage). Drives the header's persistent active underline.
    """
    request = context.get('request')
    if request is None:
        return False
    target = None
    if item.link_page_id and item.link_page:
        parts = item.link_page.get_url_parts()
        target = parts[2] if parts else None
    elif item.link_url:
        target = item.link_url
    if not target or not target.startswith('/'):
        return False
    if target == '/':
        return request.path == '/'
    return request.path == target or request.path.startswith(target.rstrip('/') + '/')


@register.simple_tag()
def get_topics_panel():
    """
    The header "Topics" mega-menu, rendered live from the research taxonomy:
    one column per live ThemePage (taxonomy order) with its programs (ThemeProgram
    display labels) and a "Learn More" link to the theme. Mirrors the data source
    used by Program Spotlight, so the nav never needs hand-maintaining.
    """
    from research.models import ThemePage  # local: research imports menus indirectly
    from django.utils.html import strip_tags

    def rel(page):
        # Relative path, not page.url (which has no request here and falls back to
        # the Site's absolute root_url — links would point at www.cigionline.org
        # off-prod). get_url_parts()[2] is the path only.
        parts = page.get_url_parts()
        return parts[2] if parts else page.url

    panel = []
    themes = (
        ThemePage.objects.live().filter(archive=0).order_by('path')
        .prefetch_related('theme_programs__program')
    )
    for theme in themes:
        programs = []
        for row in theme.theme_programs.all():
            program = row.program
            if program and program.live and getattr(program, 'archive', 0) != 1:
                programs.append({'title': row.display_title, 'url': rel(program)})
        panel.append({
            'title': theme.title,
            'description': strip_tags(theme.description or '').strip(),
            'url': rel(theme),
            'programs': programs,
        })
    return panel

from django import template

register = template.Library()


@register.inclusion_tag('includes/ds_icon.html')
def ds_icon(name, css_class=''):
    """Render a shared design-system inline SVG icon from a single source
    (includes/ds_icon.html) — no pasted SVG across templates.

    Usage: ``{% ds_icon 'chevron-right' css_class='ds-carousel-nav__icon' %}``.
    """
    return {'name': name, 'css_class': css_class}

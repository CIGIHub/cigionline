from django.utils.html import format_html
from core.models import Theme


def title_with_actions(obj):
    if hasattr(obj, 'title') and obj.title:
        return format_html(
            '<div class="title">'
            '   <div class="title-wrapper">'
            '       <strong><a href="{url}">{title}</a></strong><br>'
            '   </div>'
            '   <ul class="actions">'
            '       <li>'
            '           <a class="button button-secondary button-small" href="{edit_url}">Edit</a>'
            '       </li>'
            '       <li>'
            '           <a class="button button-secondary button-small" href="{live_url}" target="_blank">View</a>'
            '       </li>'
            '   </ul>'
            '</div>',
            url=f"/admin/pages/{obj.pk}/edit/",
            title=obj.title,
            edit_url=f"/admin/pages/{obj.pk}/edit/",
            live_url=obj.url if hasattr(obj, "url") else "#"
        )
    elif type(obj) is Theme:
        # Fallback for objects that do not have a title but have a name
        return format_html(
            '<div class="title">'
            '   <div class="title-wrapper">'
            '       <strong><a href="{url}">{name}</a></strong><br>'
            '   </div>'
            '   <ul class="actions">'
            '       <li>'
            '           <a class="button button-secondary button-small" href="{edit_url}">Edit</a>'
            '       </li>'
            '   </ul>'
            '</div>',
            url=f"/admin/snippets/core/theme/edit/{obj.pk}/",
            name=obj.name,
            edit_url=f"/admin/snippets/core/theme/edit/{obj.pk}/",
        )
    return 'No Title Available'


def live_icon(obj):
    if obj.live:
        return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
    else:
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')


def archive_icon(obj):
    if obj.archive:
        return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
    else:
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')


def person_types(obj):
    return ', '.join([ptype.name for ptype in obj.person_types.all()]) if obj.person_types.exists() else 'None'

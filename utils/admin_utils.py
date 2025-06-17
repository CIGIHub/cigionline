from django.utils.html import format_html


def title_with_actions(obj):
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


def live_icon(obj):
    if obj.live:
        return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
    else:
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')

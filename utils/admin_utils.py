from django.utils.html import format_html
from core.models import Theme
from menus.models import Menu
from promotions.models import PromotionBlock
from signals.models import PublishEmailNotification


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
    else:
        # Handle specific types with their own display logic
        type_map = {
            Theme: {
                "url": lambda o: f"/admin/snippets/core/theme/edit/{o.pk}/",
                "display": lambda o: o.name,
                "edit_url": lambda o: f"/admin/snippets/core/theme/edit/{o.pk}/",
                "actions": True,
            },
            Menu: {
                "url": lambda o: f"/admin/snippets/menus/menu/edit/{o.pk}/",
                "display": lambda o: o.name,
                "edit_url": lambda o: f"/admin/snippets/menus/menu/edit/{o.pk}/",
                "actions": True,
            },
            PromotionBlock: {
                "url": lambda o: f"/admin/snippets/promotions/promotionblock/edit/{o.pk}/",
                "display": lambda o: o.name,
                "edit_url": lambda o: f"/admin/snippets/promotions/promotionblock/edit/{o.pk}/",
                "actions": True,
            },
            PublishEmailNotification: {
                "url": lambda o: f"/admin/snippets/signals/publishemailnotification/edit/{o.pk}/",
                "display": lambda o: o.user,
                "edit_url": lambda o: f"/admin/snippets/signals/publishemailnotification/edit/{o.pk}/",
                "actions": True,
            },
        }
        obj_type = type(obj)
        if obj_type in type_map:
            conf = type_map[obj_type]
            return format_html(
                '<div class="title">'
                '   <div class="title-wrapper">'
                '       <strong><a href="{url}">{display}</a></strong><br>'
                '   </div>'
                '   <ul class="actions">'
                '       <li>'
                '           <a class="button button-secondary button-small" href="{edit_url}">Edit</a>'
                '       </li>'
                '   </ul>'
                '</div>',
                url=conf["url"](obj),
                display=conf["display"](obj),
                edit_url=conf["edit_url"](obj),
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

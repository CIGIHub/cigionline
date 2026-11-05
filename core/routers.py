"""Shared helpers for the design-system router pages (faceted CPT listings).

All routers render the same `.ds-router` chrome and a shared, swappable results
partial. On a normal request the page renders in full; on an in-place filter the
front-end (`router.js`) refetches the same URL with an `X-Requested-With` header
and the page returns ONLY the results partial as JSON — no React, no separate
endpoint. Progressive enhancement: with JS off the GET form full-reloads.
"""

from django.http import JsonResponse
from django.template.loader import render_to_string


def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def router_partial_response(request, context):
    """Render just the results partial (grid + pager or empty state) + the meta
    the front-end needs to update the count. `context` is the page's normalized
    router context (see the `router_*` keys the templates consume)."""
    html = render_to_string('includes/router_results_partial.html', context, request=request)
    page = context.get('router_page')
    return JsonResponse({
        'html': html,
        'total': context.get('router_total', 0),
        'rangeStart': context.get('router_range_start', 0),
        'rangeEnd': context.get('router_range_end', 0),
        'pageCount': page.paginator.num_pages if page else 1,
    })


class RouterServeMixin:
    """Wagtail page mixin: return the results partial for AJAX filter requests,
    the full page otherwise.

    Two shapes are supported:

    - **Page-level router** (Events / Experts / Annual Reports): the page's
      `get_context` populates the shared `router_*` keys and there is one router
      per page. The AJAX request carries no `router=` param, so we just re-render
      `get_context`.
    - **Block-level faceted listings** (decision D4): a page may host one or more
      faceted-listing blocks (in its body, or nested in a composable Tabs block),
      each owning a stable `prefix`. An AJAX request carries `router=<prefix>`; we
      locate that block's value and build *only* its listing context, so two
      listings on one page never collide.
    """

    def serve(self, request, *args, **kwargs):
        if is_ajax(request):
            prefix = request.GET.get('router')
            if prefix:
                from core.faceted_listing import (
                    build_listing_context, find_faceted_listing_value,
                )
                value = find_faceted_listing_value(self, prefix)
                if value is not None:
                    context = build_listing_context(request, value, page=self)
                    return router_partial_response(request, context)
            return router_partial_response(request, self.get_context(request))
        return super().serve(request, *args, **kwargs)


def pager_range(page_obj, window=5):
    """Page numbers for the shared router pager (BugHerd #431 — Jennifer: "show
    pages up to five and then last page, as on the current website").

    A window of up to ``window`` consecutive numbers around the current page (the
    legacy Paginator.js rule), then ``…`` + the last page when the last page falls
    outside the window, and ``1`` + ``…`` in front when the first page does.
    Yields ints and ``Paginator.ELLIPSIS`` like ``get_elided_page_range`` so
    ``includes/router_pager.html`` needs no change.
    """
    paginator = page_obj.paginator
    total, current = paginator.num_pages, page_obj.number
    if total <= window:
        return list(range(1, total + 1))
    start = max(1, min(current - window // 2, total - window + 1))
    end = start + window - 1
    numbers = list(range(start, end + 1))
    if start > 1:
        numbers = [1, paginator.ELLIPSIS] + numbers if start > 2 else [1] + numbers
    if end < total:
        numbers = numbers + [paginator.ELLIPSIS, total] if end < total - 1 else numbers + [total]
    return numbers

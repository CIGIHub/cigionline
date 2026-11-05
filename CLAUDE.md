# CIGI redesign — working instructions

The site is rebuilt on a shared design-system (DS) component library in Wagtail;
the existing backend and content are reused. See
[docs/redesign/README.md](docs/redesign/README.md) for how the system is
organized — modules, the shared card, surfaces, and where things live in code.

## Before building UI

Reuse before adding. Most layouts are a variant of an existing DS module or the
shared `card` (`templates/includes/card.html`). Check `streams/blocks.py` and
`templates/streams/` for a block that already covers the design before creating a
new one. Presentation logic lives in `core/` (`heroes.py`, `cards.py`,
`queries.py`, `routers.py`, `faceted_listing.py`); styles in
`cigionline/static/css/design-system/`; behaviour in
`cigionline/static/js/design-system/`.

Keep [docs/redesign/README.md](docs/redesign/README.md) accurate when the module
set or page-type status changes.

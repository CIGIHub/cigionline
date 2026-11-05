# CIGI redesign

The CIGI website rebuilt on a shared design-system (DS) component library in
Wagtail. The existing backend and content are reused unchanged; this work
re-skins the front end and adds the new listing pages. Data-model changes are
additive only.

## How pages are built

A page is composed of DS **modules** placed in its `body` StreamField. Modules
are defined as StreamField blocks in `streams/blocks.py` and rendered by
templates in `templates/streams/`. The full module library ships in the
default body (`BasicPageAbstract.body_module_blocks`), so every page type
offers it unless the model overrides `body` (detail pages like EventPage do). Most layouts are a variant of the shared
**card** (`templates/includes/card.html`) — build a new layout as a card variant
or an existing module before adding a new component.

Presentation logic lives in `core/`: `heroes.py`, `cards.py`, `queries.py`,
`routers.py`, `faceted_listing.py`. Styles are in
`cigionline/static/css/design-system/` (compiled into the `cigionline` webpack
bundle, loaded site-wide by `base.html`); behaviour is in
`cigionline/static/js/design-system/`. Design tokens are defined in
`_tokens.scss` and drive two colour modes (light/dark) plus four topic accents.

## Modules

- **Heroes** — primary, secondary (`alt_hero`), branded (`split_hero`), and the
  per-page-type content heroes. Content singles (article, publication, event,
  multimedia) tagged to a current program trail Home > Theme > Program; the
  rest trail Home > the archive page, found via Settings → Archive or, when
  blank, the live Basic page with an archive-mode Faceted Listing
  (`core/archive.py`; BugHerd #279). An episode filed under a live series
  keeps Home > Series. No crumb links a topic page. Article and
  publication heroes sit in 7-day fragment caches, so an archive rename
  reaches them when those expire or are flushed.
- **Content** — banner, CTA, image+text, stats, accordion, tabs, text columns,
  text-card grid, gallery, video+text, supporting-materials carousel, video
  carousel.
- **Dynamic** (auto-query, or hand-pick) — program spotlight, program grid,
  programs carousel, resource bento, resource carousel, events carousel, experts
  grid, experts carousel, news grid, trending-issues banner, jobs list.
- **Listings** — one faceted-listing module (`core/faceted_listing.py` +
  `templates/includes/router_*`) reused per archive, scoped by
  type/subtype/program. Program source "Archive — content with no program"
  lists everything outside the current-IA programs (the Archive page).
  Card pills are always the page's topics, never its program (Evan,
  2026-09-22; `core/cards.py:page_pills`). Each is a link into its theme
  page's resource listing with the topic pre-selected (`core/router_links.py`;
  the theme is `TopicPage.program_theme`, the listing is the theme page's
  first Faceted Listing — top-level or in a Tabs panel). A topic with no
  theme, or a theme page with no listing, pills plain. Program pills survive
  in the expert hero's programs row and in the content hero of a page with no
  topics, both via `project_pills` (theme-mapped programs only; BugHerd #514).
  Program modules (Spotlight, Program Grid, Programs Carousel) no longer pill
  programs: content cards show topics; a card that is a program page, and the
  Spotlight panel, show none (`streams/blocks.py:program_card_pills`; BugHerd
  #519).

## Page types

Single templates exist for every content type (article, publication, event,
podcast, expert, news); their DS heroes are wired and the shared reading body is
being re-skinned.

Listings live for events, experts, CIGI news, in-the-news, annual reports, the
global search page, the program resource hubs, and the DPH hub tabs. The
homepage is a composed DS body on `home.HomePage.body` — seed a default with
`python manage.py seed_homepage --apply`.

## Authoring notes

- [authoring-guide.md](authoring-guide.md) documents every DS module for
  editors: options, editing UI, auto/manual modes, surfaces and the faceted
  listing's card types/scopes/facets.
- Compose a page by adding modules to its body in the Wagtail admin.
- Dynamic modules populate themselves (recent content, all experts, a program's
  pages) when left empty, or take a hand-picked list.
- Listings query the ORM; the global search page uses Elasticsearch.
- Header dropdowns come from the `primary-nav` menu (Settings → Menus). A
  menu's optional **Bottom link** renders as a full-width link under its
  dropdown (desktop) and as the last link of its drawer section (phones);
  `includes/_nav_bottom_link.html`, BugHerd #539.

## Close-out

One dev week remains (from 2026-07-08). [close-out.md](close-out.md) is the
punch list: staging-push steps, the remaining dev items, QA, and the
editorial track. Scope authority is the Keypage R03 audit
([keypage-r03-authority.md](keypage-r03-authority.md)).

## QA

[qa-catalogue.md](qa-catalogue.md) is the sign-off sheet: every page type,
module, router and form with test URLs, design nodes, caveats and a QA
checkbox. Per-change verification detail lives in
[qa-test-pages.md](qa-test-pages.md).

## Before launch

- Re-skin the shared single-page reading body across the content types.
  Remaining legacy in-body blocks are scoped in
  [block-tail-catalogue.md](block-tail-catalogue.md) (per-instance list:
  [block-tail-instances.csv](block-tail-instances.csv)); page-level field
  gaps per single are scoped in
  [single-field-parity.md](single-field-parity.md).
- Build and wire the podcast series/router.
- Load the legacy→new redirect map at cutover.
- ~~Configure editor roles and permissions~~ — closed 2026-07-08: nothing
  net-new from the rebuild needs gating; existing CIGI roles carry over
  (close-out.md #6).
- Run a WCAG 2 audit.
- Remove the `/ds-test-pages/` preview routes.

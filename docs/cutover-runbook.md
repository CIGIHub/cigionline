# CIGI redesign — cutover runbook

How to put the redesign onto production data. Required scripts must be in the
redesign code before cutover. This page gives the order to run them in.

Last reviewed: November 17, 2026.

## The code

The redesign code is on the Takt staging app, branch `main`:

```
heroku git:clone -a cigionline-staging-takt
```

## Before you deploy

1. **Confirm the selective production ports are complete.** Follow
   [`master-to-redesign-porting.md`](master-to-redesign-porting.md). Do not rely
   on the current `staging-takt` ancestry to prove that production work is
   present. Some apps contain the same migration identity with different
   operations; `makemigrations --merge` alone cannot resolve those collisions.
   Reconcile them against production's applied migration history and rehearse
   the result on a production database copy.
2. **Size the release dyno.** Deploy runs about 430 migrations through
   `bin/release-migrate.sh`. A 512 MB release dyno ran out of memory on
   staging. Use Standard-2X for the release.
3. **Back up the database.** Some steps cannot be undone without a backup.

   ```
   heroku pg:backups:capture -a <app>
   ```

4. **Rehearse on a copy of production first.**

   The events migration name `0061_alter_eventlistpage_body_alter_eventpage_body`
   collided between production and Takt. The reconciled graph keeps the exact
   production migration, replays the Takt operation as
   `0061_takt_alter_eventlistpage_body_alter_eventpage_body`, merges the branches
   at `0089`, and restores current field state at `0090`. These are field-state
   reconciliations with no new irreversible data operation, but they must be
   included in the production-copy rehearsal. Do not reuse a test database that
   recorded the old Takt file under the production `0061` identity.

   Production already records `events.0064_registrant_attended`; the port keeps
   that migration byte-for-byte and joins it to Takt with no-op merge `0091`.
   On a fresh database `0064` adds a Boolean column defaulting existing rows to
   not attended. Reversing it drops recorded attendance, so use the database
   backup if rollback must preserve attendance data.

5. **Prepare and approve the Takt content overlay.** Production remains the
   source of truth for all current and operational data. Only the explicitly
   approved, redesign-specific content described below may come from Takt
   staging. A database restore, `dumpdata`/`loaddata`, or copying Wagtail row
   primary keys from staging to production is not an acceptable merge.

## Preserve Takt-authored content

A production database refresh would erase the homepage and project-page work
that editors have completed on Takt staging. Before cutover, add a narrow pair
of management commands to export and import that work as a **content overlay**.
The exporter and importer do not exist yet; cutover is blocked until they and
their tests are merged.

### Requirements

- Keep production as the base database. The overlay must not contain users,
  permissions, event registrations, form submissions, email campaigns,
  redirects, scheduled jobs, or other operational records.
- Maintain a reviewed manifest of every page in scope and the exact fields
  staging is allowed to replace. Initial scope is the homepage's authored
  redesign fields and all approved project pages; add theme, listing, settings,
  or snippet content only when a content owner names it in the manifest.
- Identify an existing target by site, concrete page model, and a stable content
  key: use `ProjectPage.drupal_node_id` when present, otherwise the canonical
  parent path plus slug. Never use a database primary key as cross-environment
  identity. Fail on missing or ambiguous targets.
- Export page chooser, image, document, media, snippet, taxonomy, and ordered
  child relations by stable keys, then resolve them against production during
  import. Report every unresolved reference and make the import fail before it
  publishes anything.
- Create net-new project shells with `seed_net_new_programs` before import. The
  overlay fills and publishes the approved shells; it must not create a second
  page when the stable key already exists.
- Write through Wagtail revisions and publishing APIs so revisions, search
  indexing hooks, page paths, and audit history remain valid. Preserve all
  production fields not granted to the overlay.
- Default both commands to dry-run. `--apply` must run the database changes in
  a transaction, print created/updated/skipped counts, and save a machine-readable
  report containing each target and its before/after content hash. Reapplying
  the same overlay must make no further changes.
- Treat files separately from database content. Inventory referenced image,
  document, and media originals; copy only missing objects to production storage,
  verify size and checksum, and never overwrite an existing object with different
  bytes. Renditions can be regenerated.
- Keep the approved export artifact immutable and checksum it. Store it in the
  agreed secure release location rather than on a dyno's ephemeral filesystem.
  Do not include unpublished or access-restricted content unless the manifest
  explicitly calls for it.

Do not broaden this into a general-purpose environment synchronizer. It is a
one-way, allow-listed cutover operation for known editorial content.

### Build and rehearsal plan

1. Freeze redesign content entry long enough to inventory Takt staging. Record
   every in-scope page, field, live/draft state, locale, parent, relation, and
   file dependency. Have the content owner approve the manifest and representative
   screenshots before export.
2. Implement the smallest export/import commands around that manifest, with
   focused tests for stable-key matching, reference remapping, field allow-listing,
   conflict failure, idempotency, and transaction rollback.
3. Restore a fresh production backup to an isolated rehearsal app, deploy the
   cutover code, run migrations, and run the pre-overlay commands through
   `normalize_program_research_tabs` below. Do not reuse the long-lived Takt
   database as proof that the merge works.
4. Run the overlay importer without `--apply`. Resolve every missing/ambiguous
   page or dependency and review its field-level change report. A production
   edit outside the allow-list must remain unchanged; a changed allow-listed
   field requires an explicit content-owner decision.
5. Copy and verify required media, apply the overlay, and apply it a second time
   to prove it is idempotent. Then run `load_cutover_redirects`, rebuild the
   search index, clear caches, and complete the checks below.
6. Record the final artifact checksum, command output, duration, page counts,
   file counts, approver, operator, and rehearsal backup identifier here before
   scheduling production cutover.

### Production content window and rollback

- Freeze Wagtail editing on production and Takt before the final export. If an
  emergency production edit is unavoidable, repeat the dry-run conflict review
  against a new production backup.
- Capture a production backup immediately before deployment and record its ID.
  Keep the site in maintenance mode while migrations and the overlay are being
  applied so visitors and editors never see a half-imported page set.
- If the importer fails, its database transaction must roll back. Copied media
  may remain as unreferenced objects and can be cleaned up later; do not delete
  or overwrite production media during rollback.
- For a page-level editorial error, use the import-created Wagtail revision to
  restore the prior version. For migration failure, widespread bad references,
  or an unsafe partial cutover, roll code back and restore the recorded database
  backup. Rebuild the search index and clear caches after either recovery path.

## Deploy

Deploy the merged code. The release phase applies all migrations. Then check
these items in the admin:

- Each of the 4 research themes has an accent.
- Each theme page lists its programs (13 in total). Migration
  `research/0066` matches program titles exactly. It skips a title that does
  not match, with no error. Add any missing program on the theme page.

## Run once, in this order

Run each command with `heroku run -a <app> "python manage.py <command>"`.
Put the whole command in quotes. Commands with `--apply` do a dry run
without it. Run the dry run first and read the output.

| # | Command | Notes |
|---|---|---|
| 1 | `update_index` | Run first. The seed commands fail if the search index is missing. |
| 2 | `seed_homepage --apply` | Fallback only for a homepage not included in the approved overlay. It skips a homepage that already has a body. Do not use `--force` at cutover. |
| 3 | `seed_listing_pages --apply` | Fallback only for listing pages not included in the approved overlay. It skips populated bodies. Do not use `--force` at cutover. |
| 4 | `seed_net_new_programs` | Creates the 4 new program pages as drafts and links them to themes. No dry run. |
| 5 | `consolidate_topics --apply` | 26 topics to 17: 4 renames, 9 merges, redirects, and the production “India, China and Africa” program-topic backfill. Cannot be undone without the backup. |
| 6 | `update_expert_topics` | Fills expertise topics on people. No dry run. Schedule it weekly (Heroku Scheduler). |
| 7 | `clear_dph_publication_themes --apply` | Required: DPH working papers use the new design. |
| 8 | `backfill_programs --pages research/data/program-backfill-pages.csv --apply` | Only after CIGI approves the program mapping. Save the reversal CSV it writes: Heroku deletes it when the command ends. |
| 9 | `normalize_program_research_tabs --apply` | Sets the Research tab listing on program pages. |
| 10 | `<content-overlay-import> --artifact <approved-artifact>` | Run the required dry run and review its report; then repeat with `--apply`. Replace this placeholder with the implemented command and exact options before cutover. |
| 11 | `load_cutover_redirects --apply` | 7 redirects for retired listing pages. |
| 12 | `update_index` | Run again. Steps 4, 8, 10 and the migrations write without reliably reindexing every affected object. |

Then clear the template cache:

```
heroku run -a <app> "python manage.py shell -c \"from django.core.cache import caches; caches['default'].delete_pattern('*template.cache*')\""
```

## Content to do by hand

- Review the imported homepage and every project page against the approved Takt
  screenshots and overlay report. Do not recreate approved staging content by
  hand unless the overlay rollback plan has been invoked.
- Rename the people listing page "CIGI Experts" to "Experts".
- Set the thank-you pages in the email form settings.
- Check the header, footer and email form settings on the site that serves
  the pages. These settings are per site.

## Content verification

- The imported page count and set of stable keys exactly match the approved
  manifest; no unlisted production page changed.
- The homepage and every project page have the expected published revision,
  parent, URL, locale, body modules, hero, contacts, members, featured content,
  topics, theme memberships, files, and subscription link as applicable.
- Every chooser reference resolves to the intended production object. Every
  imported original image, document, and media file loads from production
  storage; required alt text and access restrictions are preserved.
- There are no duplicate project slugs, broken internal links, orphan pages,
  unpublished pages that should be live, or unintentionally published drafts.
- Anonymous and editor smoke tests pass on desktop and mobile for the homepage,
  all project pages, header/footer navigation, search, forms, redirects, and a
  representative page for each imported module type.
- The final `update_index` completed, template and application caches were
  cleared, error monitoring is quiet, and production editors can create a new
  revision without losing imported content.

## Never run on production

- `seed_module_placeholder_data` — placeholder images and subtitles.
- `seed_module_test_pages` — QA test articles.
- `backfill_gcg_program_content` — a rough test mapping. Its `--revert`
  removes every link to those programs.

Delete the QA test pages (`*-test` pages and the `/ds-test-pages/` routes)
before launch.

# CIGI redesign — cutover runbook

How to put the redesign onto production data. All scripts are in the
redesign code. This page gives the order to run them in.

## The code

The redesign code is on the Takt staging app, branch `main`:

```
heroku git:clone -a cigionline-staging-takt
```

## Before you deploy

1. **Complete the selective production ports.** Follow
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
| 2 | `seed_homepage --apply` | Default homepage layout. Skips a homepage that already has a body. |
| 3 | `seed_listing_pages --apply` | Default layouts for Events, Experts, Annual Reports, Opinions. |
| 4 | `seed_net_new_programs` | Creates the 4 new program pages as drafts and links them to themes. No dry run. |
| 5 | `consolidate_topics --apply` | 26 topics to 17: 4 renames, 9 merges, redirects. Cannot be undone without the backup. |
| 6 | `update_expert_topics` | Fills expertise topics on people. No dry run. Schedule it weekly (Heroku Scheduler). |
| 7 | `clear_dph_publication_themes --apply` | Only if CIGI wants DPH working papers on the new design. |
| 8 | `backfill_programs --pages research/data/program-backfill-pages.csv --apply` | Only after CIGI approves the program mapping. Save the reversal CSV it writes: Heroku deletes it when the command ends. |
| 9 | `normalize_program_research_tabs --apply` | Sets the Research tab listing on program pages. |
| 10 | `load_cutover_redirects --apply` | 7 redirects for retired listing pages. |
| 11 | `update_index` | Run again. Steps 4, 8 and the migrations write without reindexing. |

Then clear the template cache:

```
heroku run -a <app> "python manage.py shell -c \"from django.core.cache import caches; caches['default'].delete_pattern('*template.cache*')\""
```

## Content to do by hand

- Content made only on staging: the new program pages and their content, the
  theme, home and listing page layouts, and other staging content entry.
- Rename the people listing page "CIGI Experts" to "Experts".
- Set the thank-you pages in the email form settings.
- Check the header, footer and email form settings on the site that serves
  the pages. These settings are per site.

## Never run on production

- `seed_module_placeholder_data` — placeholder images and subtitles.
- `seed_module_test_pages` — QA test articles.
- `backfill_gcg_program_content` — a rough test mapping. Its `--revert`
  removes every link to those programs.

Delete the QA test pages (`*-test` pages and the `/ds-test-pages/` routes)
before launch.

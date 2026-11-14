# Porting production changes into the redesign

This is the working agreement for reconciling production `master` with the
Takt redesign. Read it before changing `staging-takt`, porting a production
feature, resolving migrations, or preparing cutover.

Last reviewed: November 14, 2026.

## Current state

- The real common ancestor of production and the vendor history is
  `b94f39a5` from May 20, 2026.
- `staging-takt-heroku-history` preserves the vendor's real history: 442
  commits after the common ancestor at the time of review.
- `master` had 76 commits after the common ancestor at the time of review.
- `staging-takt` is **not** a normal merge. Commit `66c2a2e3` imported the
  vendor tree as a snapshot directly on top of production commit `e614fe35`.
  Its tree matched the vendor history, but its parentage makes Git believe all
  earlier production changes are already present.
- Consequently, merging `master` into `staging-takt` can report success while
  production behaviour remains overwritten by the snapshot.
- No selective feature ports had been started when this document was written.

Recheck these facts rather than assuming the counts are still current:

```bash
git status --short --branch
git merge-base master staging-takt-heroku-history
git rev-list --left-right --count staging-takt-heroku-history...master
git log --oneline --decorate -n 10 master
git log --oneline --decorate -n 10 staging-takt
```

Do not rewrite or delete `master`, `staging-takt`, or
`staging-takt-heroku-history`. They are evidence and rollback points.

## Strategy

Port selected production capabilities into `staging-takt` through small,
reviewed branches. The unit of work is a complete feature with its fixes,
tests, migrations, configuration, templates, JavaScript, and styles—not
necessarily one Git commit.

Every production change must end in one recorded state:

- **Ported** — applied substantially as it exists on `master`.
- **Adapted** — behaviour retained but implementation changed for the redesign.
- **Superseded** — redesign already provides equivalent behaviour, verified.
- **Dropped** — intentionally excluded with a named decision owner and reason.

Silence is not a status. Do not assume a change survived because Git considers
its original commit an ancestor of `staging-takt`.

## One feature at a time

Start each port from the latest reviewed `staging-takt`:

```bash
git switch staging-takt
git switch -c port/<short-feature-name>
git cherry-pick --no-commit <source-commit>
```

For a feature with follow-up fixes, apply all required commits in chronological
order with `--no-commit`. Before committing:

1. Read every source commit and list its affected callers, tests, fixtures,
   settings, templates, assets, exports, and migrations.
2. Inspect the full working-tree diff. A clean cherry-pick does not prove the
   old template or frontend architecture is appropriate for the redesign.
3. Keep the production behaviour and adapt the presentation or integration
   points to existing redesign patterns.
4. Do not use blanket `ours` or `theirs` conflict resolution.
5. Reconcile migrations using the rules below.
6. Run the narrow relevant tests and build checks.
7. Commit with the original source hashes in the message or body.
8. Open a focused PR into `staging-takt`, deploy it to an isolated staging
   environment, and verify it before beginning the next feature.
9. Update the progress ledger in this document in the same PR.

Use direct cherry-picks only for genuinely isolated changes such as copy or a
small CSS fix. Models, event registration, StreamFields, security, integrations,
shared templates, and interactive frontend components require an adapted
feature port.

## Migration rules

Production's applied migration history is authoritative because the final code
must run against the production database.

- Never change the contents of a migration already applied in production.
- Never assume matching migration numbers represent matching operations.
- An exact app-and-filename collision with different contents is not fixed by
  `makemigrations --merge`; Django identifies migrations by app and name, so
  the production database may already mark the vendor operation as applied.
- Preserve the production migration identity and recreate any required vendor
  state change in a new migration after the reconciled production lineage.
- Different migration filenames that create divergent graph leaves may use a
  merge migration after their operations and dependencies are reviewed.
- Do not renumber or delete migrations casually. First determine whether each
  migration ran on production, vendor staging, both, or neither.
- Test the complete migration path against a recent copy of production. A
  fresh empty database is useful but insufficient.
- Record irreversible operations, expected runtime, release-dyno memory needs,
  and rollback requirements in `docs/cutover-runbook.md`.

Before accepting a migration-bearing port, inspect at least:

```bash
python manage.py showmigrations <app>
python manage.py makemigrations --check --dry-run
python manage.py migrate --plan
```

## Verification

Run checks proportional to the feature. The normal baseline is:

```bash
python manage.py test <affected_app>
python manage.py makemigrations --check --dry-run
npm run lint:js
npm run format:check
npm run build
```

For migration-bearing work, also migrate a restored production database. For
shared or high-risk work, run the full Django suite. For event registration,
verify forms, stored answers, guest registration, reports, admin, public
JavaScript, email rendering and sending, and existing registrant data.

Staging acceptance should exercise real Wagtail content, editor workflows,
responsive rendering, accessibility, search, forms, email, caching, and static
assets as applicable. Automated checks do not replace this review.

## Recommended order

1. One small migration-free pilot to validate the port/PR/deploy workflow.
2. Security-sensitive behaviour, especially Turnstile.
3. MediaValet and other editor integrations.
4. Event registration in dependency order: form blocks, choice limits,
   conditional questions and fixes, closing dates, attendance, reports, email.
5. Shared StreamField blocks and interactive charts.
6. Annual-report map functionality.
7. DPH and subscription behaviour.
8. Product-decision features: Human Analysis Standard and the anniversary site.
9. Remaining copy and cosmetic changes.

Keep adding new `master` work to this inventory while integration continues;
do not allow another multi-month unreviewed gap.

## Initial progress ledger

All groups were pending when this document was created. Replace **Pending**
with one of the recorded states above and add the PR, owner, and verification
notes as work is completed.

| Change group | Important source commits | Status | PR / decision / verification |
|---|---|---|---|
| AI guidance and PR template | `b967088e`, `cabeff55` | Adapted | Restored and updated for redesign paths, commands, migration reconciliation, and review disclosure. |
| Turnstile validation | `81bafe9e` | Ported | Security boundary for event, subscription, and facility forms. |
| Event form rich text | `d0363f39` | Adapted | Production migration preserved alongside the Takt branch; DS rendering adapted. Focused tests, template compilation, event migration graph, and changed-file ESLint pass. Production-clone migration planning remains blocked by pre-existing `annual_reports.0062`-before-`0061` history. |
| Event choice limits | `d3d73c76` | Ported | Production `0057` preserved and already applied on the production clone; merge `0087` joins the Takt graph. Eleven focused and all 33 event tests pass; templates compile, changed-file ESLint and the frontend build pass. The source test repairs also cleared the prior event-suite baseline failures. |
| Event conditional questions | `3635ff68`, `68c6fede`, `25156c59` | Adapted | Multiple conditional questions, ordering fix, requiredness fix, snippet preview, admin editing, email filtering, and DS field rendering retained. Exact production `0058`/`0059` migrations are preserved; merge `0088` joins the Takt graph. All 45 event tests, changed-file ESLint, migration checks, and the frontend build pass. The production clone already records `0057`–`0059`; migration planning remains blocked by its pre-existing `annual_reports.0062`-before-`0061` history. |
| Event close dates | `dd5fb93c` | Adapted | Effective per-type deadlines, invite/type URL enforcement, transaction-time deadline checks, report visibility, no-cache headers, and redesigned hero/card CTAs retained. Exact production `0060`–`0063` migrations are preserved; the colliding Takt `0061` is replayed under a new identity before its downstream migrations, merge `0089` joins the branches, and `0090` restores current redesign field state. A fresh database traverses the full graph; all 15 focused tests and all 55 event tests pass. A broader 17-test run found only the pre-existing `HomePageTests.test_homepage_child_page_types` omission of `PolicyPopupGroupPage`. The production-clone plan is valid after bypassing its separately known `annual_reports` history inconsistency; migrations have not yet been applied to that clone. Legacy React/listing changes were superseded by redesign cards and heroes. |
| Attendance and registrant reports | `f22248a7`, `3ddaf642`, `e614fe35` | Ported | Registrant attendance, permission-checked event-scoped toggling, admin/CSV display, search, column sorting, pagination, and registration-type filtering retained. Exact production `0064_registrant_attended` is preserved and already applied on the production clone; no-op `0091` joins it to the Takt graph. All 8 focused tests and all 63 event tests pass; migration drift and the production-clone plan were checked while bypassing only the separately known `annual_reports` history inconsistency. |
| Event calendar and agenda | `91f98b02`, `12ec8e3f`, `04567543` | Adapted | The agenda download was already retained in the redesign event template, so legacy Bootstrap markup was not restored. Calendar API opt-out filtering and no-cache behaviour, valid Google Calendar URLs, and live/public iCal feeds with location, full URL, safe IDs, dynamic filenames, and a one-hour fallback end time are retained through redesign components. The exact production `0058_eventpage_add_to_calendar` migration and model/admin field were carried earlier. All 11 focused tests and all 70 event tests pass; migration drift is clean. |
| Event email fixes | `9b27ff21`, `5341fbf1`, `dd87b205`, `f7684015` | Pending | Includes attachments, footer, and guest merge data. |
| MediaValet | `6b82f81c`, `16c7e35c` | Pending | Cross-app editor image chooser integration. |
| Cloudflare purge admin | `9524b726` | Pending | Preserve validation, permissions, and tests. |
| Research topic operation | `f416ad05`, `0299f02e` | Pending | Confirm whether the one-time production operation already ran. |
| Shared hero document and button blocks | `ff15f177`, `8b357761` | Pending | High migration overlap across page apps. |
| Interactive charts | `2130f388` | Pending | Includes Chart.js, CSV parsing, templates, styles, and migrations. |
| Content type additions | `58b7aaff` | Pending | Report/submission choices and annual-report slide cleanup. |
| Annual-report map | `f10899d6`, `907bf3de`, `40509a90`, `ff20b238`, `09035dff`, `4d882e9c` | Pending | Includes Leaflet/geopy, GeoJSON, migrations, styling, and later fixes. |
| Human Analysis Standard | `1e42fe74`, `4e1a3af2`, `381be1ac`, `f89b757d`, `e6019290`, `c2bf46ed`, `1c0672f7` | Pending | Product decision required; page and article disclaimer are coupled. |
| Twenty-fifth anniversary | `40339e7f` plus its follow-ups | Pending | Product decision required; preserve its full migration chain if retained. Follow-ups: `337706bd`, `e388e828`, `8d2444d6`, `554ad606`, `f0cef541`, `a550225f`, `2eb9562a`, `77529ded`, `ceea1fc3`, `90fe4f03`, `25029c16`, `b288b56c`, `39e38615`, `8dc1831a`, `8ef7f190`. |
| DPH subscription and themed behaviour | `e660a3e2`, `132c5cb2`, `3e8ed6f9`, `9e112d14` | Pending | Adapt behaviour to redesigned footer, sidebar, and blocks. |
| Responsible Technology theme | `1ea73e2b` | Pending | Confirm whether still active. |
| Shared footer, icons, and social links | `eccf89b2`, `ad58b003`, `1a929cc1` | Pending | Adapt rather than restoring legacy markup wholesale. |
| Policy Prompt changes | `c4da3de4`, `23563b2a` | Pending | Episode download action and follow-up fix. |
| Multimedia link wrapping | `582775a7` | Ported | Candidate migration-free pilot. |
| RSS feed | `b7482ee4` | Pending | Added after the original inventory; inspect related URL and feed changes. |
| DPH sidebar updates | `8584374a`, `6b791bad`, `8ad8bca1`, `07ea26e6` | Pending | Reconcile copy against current approved content. |

## Definition of done

The integration is ready for final cutover only when:

- every production change group has an explicit ledger status;
- every intentional drop has an owner and reason;
- production migration identities have been reconciled and rehearsed;
- required tests and frontend builds pass;
- the redesign QA catalogue and production regression cases pass;
- forms, email, search, editor workflows, accessibility, and responsive pages
  have been checked on staging;
- database backup, code rollback, migration recovery, monitoring, and ownership
  are documented in the cutover runbook.

The final merge should be routine evidence collection, not the point at which
missing production behaviour is discovered.

# Agent instructions

## Always read first

- `docs/master-to-redesign-porting.md` — current branch topology, the plan for
  selectively porting production changes into the redesign, migration safety
  rules, progress ledger, and verification requirements.
- `.github/copilot-instructions.md`, when present on the current branch —
  repository architecture, commands, deployment notes, and conventions.

## Related instructions

- Read `docs/cutover-runbook.md` before deployment or production cutover work.
- Read `docs/registration-system.md` before changing event registration.
- Read `docs/redesign/README.md` before changing redesign architecture or
  components.
- When present, read `.github/instructions/events.instructions.md` for work
  under `events/**`, `.github/instructions/templates.instructions.md` for work
  under `templates/**`, and
  `.github/instructions/wagtail-models.instructions.md` for models or
  migrations.

Keep changes scoped, follow existing project patterns, and run the narrowest
relevant tests. Never treat Git ancestry alone as proof that a production
change survived the redesign snapshot import.

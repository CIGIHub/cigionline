# Agent Instructions

This repository keeps AI-agent guidance in `.github/`. Use this file as the root entry point.

## Always Read First

- `.github/copilot-instructions.md` - repository overview, architecture, development commands, deployment notes, and broad project conventions.

## Path-Specific Instructions

Read these when the task touches matching files:

- `.github/instructions/events.instructions.md` - event registration, registrants, invites, email templates, registration forms, and anything under `events/**`.
- `.github/instructions/templates.instructions.md` - Django/Wagtail templates, includes, stream block templates, and email templates under `templates/**`.
- `.github/instructions/wagtail-models.instructions.md` - Wagtail page models, model mixins, StreamFields, admin panels, and migrations matching `*/models.py` or `*/migrations/*.py`.

## Reusable Task Prompts

These are task templates. Use them when the user request matches the task, or when the user explicitly asks for the prompt:

- `.github/prompts/new-wagtail-page.prompt.md` - scaffold a new Wagtail page type.
- `.github/prompts/new-registration-field.prompt.md` - add a new event registration field type.
- `.github/prompts/write-tests.prompt.md` - add or expand tests.

## General Workflow

- Prefer existing project patterns over new abstractions.
- Keep changes scoped to the task.
- When editing Django/Wagtail models, create migrations and update templates/tests as needed.
- When changing event registration behavior, check all affected surfaces: forms, storage, reports, admin, public JavaScript, templates, emailing, and tests.
- Run the narrowest relevant tests or explain why they could not be run.

#!/usr/bin/env bash
# Release-phase migrations, one app per process.
#
# The release dyno is Standard-1X (512MB). A single `migrate` run holds the whole
# migration graph — 900+ files, 19MB of source, most of it StreamField `alter
# body` definitions — and then accumulates on top of that as it applies each one.
# Release v89 (2026-08-18) crossed R14 at 778MB, reached 1047MB (204% of quota)
# and took a SIGKILL mid-migration.
#
# Applying app by app keeps the graph cost but drops the accumulation: each
# process exits and returns its memory. The final catch-all `migrate` applies
# anything the per-app passes left and is the command whose exit status counts.
set -euo pipefail

# Pending lines read "[ ]  app.0001_name". Strip the marker before splitting —
# the space inside the brackets is a field separator, so $2 is not the name.
apps=$(python manage.py showmigrations --plan \
  | awk '/^\[ \]/ { line = $0; sub(/^\[ \][[:space:]]+/, "", line);
                    split(line, part, "."); print part[1] }' \
  | awk '!seen[$0]++')

if [ -z "$apps" ]; then
  echo "release: no pending migrations"
else
  for app in $apps; do
    echo "release: migrating $app"
    python manage.py migrate "$app" --noinput
  done
fi

python manage.py migrate --noinput

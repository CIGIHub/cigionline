#!/usr/bin/env bash
set -ex
if [[ -n "${BASIC_AUTH_USER}" && -n "${BASIC_AUTH_PASSWORD}" ]]; then
  echo -e "${BASIC_AUTH_USER}:$(perl -le 'print crypt($ENV{"BASIC_AUTH_PASSWORD"}, rand(0xffffffff));')" > "${HOME}/config/.htpasswd"
fi

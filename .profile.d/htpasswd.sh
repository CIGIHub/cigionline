#!/usr/bin/env bash
set -ex

echo -e "${BASIC_AUTH_USER}:$(perl -le 'print crypt($ENV{"BASIC_AUTH_PASSWORD"}, rand(0xffffffff));')" > "${HOME}/nginx/.htpasswd"

#!/usr/bin/env bash

set -euo pipefail

SSH_SERVER="haligh@ssh.pythonanywhere.com"
PATH_TO_DIST="/home/haligh/kennerliga/api"

npm run build
ssh "$SSH_SERVER" "rm -rf '$PATH_TO_DIST/dist/spa.new' && mkdir -p '$PATH_TO_DIST/dist'"
scp -r ../api/dist/spa "$SSH_SERVER:$PATH_TO_DIST/dist/spa.new"

ssh "$SSH_SERVER" << EOF
set -e
rm -rf "$PATH_TO_DIST/dist/spa.previous"
if [ -d "$PATH_TO_DIST/dist/spa" ]; then
    mv "$PATH_TO_DIST/dist/spa" "$PATH_TO_DIST/dist/spa.previous"
fi
mv "$PATH_TO_DIST/dist/spa.new" "$PATH_TO_DIST/dist/spa"
source .virtualenvs/kennerliga-venv/bin/activate
cd "$PATH_TO_DIST"
./prod_manage.py collectstatic --no-input --clear
touch /var/www/www_kennerliga_de_wsgi.py
EOF

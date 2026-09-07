#!/usr/bin/env bash

SSH_SERVER=haligh@ssh.pythonanywhere.com

ssh "$SSH_SERVER" << 'EOF'
touch /var/www/www_kennerliga_de_wsgi.py
EOF
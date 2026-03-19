#!/usr/bin/env bash

SSH_SERVER=haligh@ssh.pythonanywhere.com

ssh "$SSH_SERVER" << 'EOF'
touch /var/www/haligh_pythonanywhere_com_wsgi.py
EOF
SSH_SERVER=haligh@ssh.pythonanywhere.com
PATH_TO_DIST=/home/haligh/kennerliga/api

rm -rf dist
npm run build
ssh $SSH_SERVER "mkdir -p $PATH_TO_DIST/dist"
ssh $SSH_SERVER "rm -rf $PATH_TO_DIST/dist/spa"
scp -r dist/spa $SSH_SERVER:$PATH_TO_DIST/dist/spa

ssh $SSH_SERVER << 'EOF'
source .virtualenvs/kennerliga-venv/bin/activate
cd kennerliga/api
./prod_manage.py collectstatic --no-input

# Reload PythonAnywhere web app
touch /var/www/haligh_pythonanywhere_com_wsgi.py
EOF


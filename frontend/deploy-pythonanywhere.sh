SSH_SERVER=haligh@ssh.pythonanywhere.com
PATH_TO_DIST=/home/haligh/kennerliga/api

rm -rf dist
npm run build
# ssh $SSH_SERVER 'rm -rf $PATH_TO_DIST/dist'
scp -r dist $SSH_SERVER:$PATH_TO_DIST


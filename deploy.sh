#! /usr/local/bin/bash
#set -x
BRANCH=`git branch | sed -n -e 's/^\* \(.*\)/\1/p'`
echo you are on $BRANCH

if [ $BRANCH == 'main' ]; then
  find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
  rm -f htmshop.zip
  zip -qr htmshop.zip ecommerce requirements.txt manage.py static templates fixtures
  scp htmshop.zip transylvania.bostonmonks.com:/tmp/
  ansible-playbook -i devops/inventory.ini devops/playbooks/deploy.yml
else
  echo You must be on release branch
  exit 1
fi

#!/usr/bin/env bash

BRANCH=`git branch | sed -n -e 's/^\* \(.*\)/\1/p'`
echo you are on $BRANCH

# find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
# rm -f htmshop.zip
# poetry export -f requirements.txt --with dev --without-hashes > requirements.txt
# zip -qr htmshop.zip ecommerce requirements.txt manage.py static templates
# scp htmshop.zip transylvania.bostonmonks.com:/tmp/
# rm requirements.txt
ansible-playbook -i devops/inventory.ini devops/playbooks/deploy.yml

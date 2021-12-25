#!/usr/local/bin/bash

pyclean () {
    find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
}

pyclean
zip -qr htmshop.zip ecommerce appspec.yml requirements.txt manage.py static templates
scp htmshop.zip transylvania.bostonmonks.com:~

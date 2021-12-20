#! /usr/local/bin/bash
ansible htmstore_dev -i inventory.ini -m systemd -a "service=gunicorn state=restarted" -K

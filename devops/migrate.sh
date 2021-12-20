#! /usr/local/bin/bash
ansible htmstore_dev -i inventory.ini -m community.general.django_manage -a "virtualenv=/home/ubuntu/htmshop_django_depl/venv project_path=/home/ubuntu/htmshop_django_depl command=migrate"

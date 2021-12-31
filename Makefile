deploy : build setup
	scp htmshop.zip transylvania.bostonmonks.com:~
	ansible-playbook -i devops/inventory.ini devops/playbooks/deploy.yml

build : clean
	zip -qr htmshop.zip ecommerce requirements.txt requirements_dev.txt manage.py static templates

setup :
	ansible-playbook -i devops/inventory.ini devops/playbooks/general-setup.yml

clean :
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	rm -f htmshop.zip

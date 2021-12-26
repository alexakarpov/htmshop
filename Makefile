deploy : build
	scp htmshop.zip transylvania.bostonmonks.com:/home/storeadmin/deployment

build : clean
	zip -qr htmshop.zip ecommerce appspec.yml requirements.txt manage.py static templates

clean :
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	rm -f htmshop.zip

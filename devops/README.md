default backend

dev:

```
python manage.py runserver 4000
```

staging/prod:

```
gunicorn backend.wsgi:application -b 127.0.0.1:4000
```

(nginx listens on port 8000, transfers to Django API; this should all be run by an ansible playbook)

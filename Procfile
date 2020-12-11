release: python manage.py makemigrations codenames
release: python manage.py migrate
web: gunicorn cn_web.wsgi --log-file -

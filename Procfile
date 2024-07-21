release: python manage.py makemigrations catalogue && python manage.py migrate
web: gunicorn app.wsgi --log-file -
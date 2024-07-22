release: python manage.py makemigrations catalogue && python manage.py migrate && echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').exists() else print('Superuser already exists')" | python manage.py shell
web: gunicorn app.wsgi --log-file -

# Create migration files from model changes
python manage.py makemigrations

# Apply migrations to the database
python manage.py migrate

# Run development server
python manage.py runserver 8080

# Create superuser for admin panel
python manage.py createsuperuser

# Collect static files into STATIC_ROOT (useful for production)
python manage.py collectstatic
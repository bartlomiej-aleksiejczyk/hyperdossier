# How to install

1. Put `prototype_setup` in INSTALLED_APPS and is before django.contrib.admin:

```python
INSTALLED_APPS = [
    ...
    "prototype_setup",
    "django.contrib.admin",
    ...
]
```
Add also this
```python
AUTH_USER_MODEL = "prototype_setup.CustomizedUser"
```
And this
```python
CLIENT_COMPONENT_SETTINGS = {
    "MANIFEST_FILE_PATH": "client_components__dist/.vite/manifest.json",
    "CLIENT_COMPONENTS_PATH": "client_components/",
}
```
You can customized urls displayed in admin topbar
```python
ADMIN_CUSTOM_USERLINKS = [
    {"label": "Docs", "url": "https://docs.example.com"},
    {"label": "API", "url_name": "api-root"},
    {"label": "Transactions", "url_name": "finances:transaction_list"},
    {"label": "Contact", "url": "mailto:me@example.com"},
    {"label": "User 42", "url_name": "users:detail", "args": [42]},
]
```

And also:
```python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
```

2. What is contained in this app
- a custom user model
- an admin template for override 
- a base template
- a vite integration
- a simple fail2ban implementatin
- media and static files handling
- huey

3. TODO:
- harden security
- Prod, dev, local-prod container setup
- remove customized user
- Make a copier template of of that, add siteadmin
- finish vite integration

4. Huey setup

```python
INSTALLED_APPS = [
    ...
    "django_q",
]
Q_CLUSTER = {
    'name': 'DjangORM',
    'workers': 2,
    'timeout': 90,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default'
}
```
run q2
```python
python manage.py qcluster
```
from django.apps import apps
from hyperadmin.admin import hyperadmin

app = apps.get_app_config('finances')

for model_name, model in app.models.items():
    hyperadmin.register(model)

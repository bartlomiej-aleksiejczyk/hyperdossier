from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from hyperadmin.hyperadmin import HyperadminSite


hyperadmin = HyperadminSite(name='admin')

def autoregister_app_models(app_label: str, site: HyperadminSite):
    app_config = apps.get_app_config(app_label)
    for model in app_config.get_models():
        try:
            site.register(model)
        except AlreadyRegistered:
            # ignore if manually registered somewhere else
            pass

autoregister_app_models("auth", hyperadmin)
autoregister_app_models("django_q", hyperadmin)

def export_everything(modeladmin, request, queryset):
    # modeladmin is the ModelAdmin instance for the current model
    # request is the HttpRequest
    # queryset is the selected objects of *that* model
    # do your export here
    pass

export_everything.short_description = "Export all data"  # label in the dropdown

# register as a global action for this AdminSite
hyperadmin.add_action(export_everything, name="export_everything")
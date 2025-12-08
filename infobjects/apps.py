from django.apps import AppConfig
from django.template.response import TemplateResponse
from hyperadmin.hooks import register_admin_action, register_admin_view


def make_system_dashboard_view(admin_site):
    def view(request):
        context = dict(
            admin_site.each_context(request),
            title="System dashboard",
            stats={
                "users": 123,
                "orders": 456,
            },
        )
        return TemplateResponse(
            request,
            "hyperadmin/system_dashboard.html",
            context,
        )

    return view


def export_everything(modeladmin, request, queryset):
    pass


class InfobjectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "infobjects"

    def ready(self):
        register_admin_view("dashboard/", make_system_dashboard_view, name="dashboard")
        register_admin_action(export_everything, name="export_all")

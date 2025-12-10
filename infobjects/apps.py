from django.apps import AppConfig
from django.template.response import TemplateResponse
from iommi import Style, register_style
from iommi.path import register_path_decoding
from iommi.style_base import base
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
        from .models import Category

        register_admin_view("dashboard/", make_system_dashboard_view, name="dashboard")
        register_admin_action(export_everything, name="export_all")
        register_path_decoding(
            category_pk=Category,
        )
        register_style("infobjects_style", Style(base, base_template='infobjects/infobjects_layout.html'))

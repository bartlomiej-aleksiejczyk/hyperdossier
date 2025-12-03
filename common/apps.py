from django.apps import AppConfig

from hyperadmin.hooks import register_admin_autoreg, register_admin_sidebar_modules


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'
    verbose_name = "Customized Settings"

    def ready(self):
        from . import signals
        register_admin_autoreg("auth")
        register_admin_sidebar_modules({
            "id": "reports",
            "title": "Reports",
            "items": [
                {"label": "Finance report", "url_name": "finances:transaction_list"},
            ],
        })
        register_admin_sidebar_modules({
            "id": "tools",
            "title": "Tools",
            "items": [
                {"label": "System dashboard", "url_name": "admin:dashboard"},
                {"label": "Background tasks", "url_name": "finances:transaction_list"},
            ],
        })
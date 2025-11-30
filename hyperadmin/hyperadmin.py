import logging
from django.contrib.admin import AdminSite
from django.urls import NoReverseMatch, path, reverse
from django.template.response import TemplateResponse

logger = logging.getLogger(__name__)
# TODO: Split clas for parts that should be set externally/cusotmized and non customizable parts
class HyperadminSite(AdminSite):
    site_header = "Hyperadmin"
    site_title = "Hyperadmin"

    EXTRA_MODULES = [
        {
            "id": "tools",
            "title": "Tools",
            "items": [
                {"label": "System dashboard", "url_name": "admin:dashboard"},
                {"label": "Background tasks", "url_name": "admin:django_q_cluster_changelist"},
            ],
        },
        {
            "id": "reports",
            "title": "Reports",
            "items": [
                {"label": "Finance report", "url_name": "finances:transaction_list"},
            ],
        },
    ]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("dashboard/", self.admin_view(self.system_dashboard_view), name="dashboard"),
        ]
        return my_urls + urls

    def system_dashboard_view(self, request):

        context = dict(
            self.each_context(request),
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
    def each_context(self, request):
        context = super().each_context(request)
        context["extra_modules"] = self.get_extra_modules(request)
        return context

    def get_extra_modules(self, request):
            """
            Turn EXTRA_MODULES (with url_name) into a list that templates can use:
            [
            {
                "id": "tools",
                "title": "Tools",
                "items": [
                {"label": "System dashboard", "url": "/admin/system-dashboard/"},
                ...
                ]
            },
            ...
            ]
            """
            modules = []

            for module in self.EXTRA_MODULES:
                items = []
                module_id = module.get("id")

                for item in module.get("items", []):
                    url_name = item.get("url_name")

                    if not url_name:
                        logger.warning(
                            "Hyperadmin extra_modules: item without url_name "
                            "(module_id=%r, item=%r, user=%r)",
                            module_id,
                            item,
                            getattr(request, "user", None),
                        )
                        continue

                    try:
                        url = reverse(url_name)
                    except NoReverseMatch as exc:
                        logger.warning(
                            "Hyperadmin extra_modules: could not reverse url_name=%r "
                            "in module_id=%r (user=%r): %s",
                            url_name,
                            module_id,
                            getattr(request, "user", None),
                            exc,
                        )
                        continue

                    items.append(
                        {
                            "label": item.get("label", url_name),
                            "url": url,
                        }
                    )

                if (len(items)) > 0:
                    modules.append(
                        {
                            "id": module_id,
                            "title": module.get("title"),
                            "items": items,
                        }
                    )

            return modules


from django.contrib.admin import AdminSite
from django.urls import NoReverseMatch, path, reverse
from django.template.response import TemplateResponse

class HyperadminSite(AdminSite):
    site_header = "Hyperadmin"
    site_title = "Hyperadmin"

    EXTRA_MODULES = [
        {
            "id": "tools",
            "title": "Tools",
            "items": [
                {"label": "System dashboard", "url_name": "admin:system-dashboard"},
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
            path("dashboard/", self.admin_view(self.system_dashboard_view), name="metrics"),
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
            "admin/system_dashboard.html",
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
            for item in module.get("items", []):
                url_name = item.get("url_name")
                try:
                    url = reverse(url_name)
                except NoReverseMatch:
                    # Skip missing URLs rather than crashing
                    continue

                items.append(
                    {
                        "label": item.get("label", url_name),
                        "url": url,
                    }
                )

            modules.append(
                {
                    "id": module.get("id"),
                    "title": module.get("title"),
                    "items": items,
                }
            )

        return modules

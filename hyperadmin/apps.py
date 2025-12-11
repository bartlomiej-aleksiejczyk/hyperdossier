from django.apps import AppConfig
from django.urls import reverse

from search.providers import register_global_search_provider


def admin_provider_factory(admin_site):
    def admin_search_provider(request, query):
        results = []

        for model, model_admin in admin_site._registry.items():
            search_fields = model_admin.get_search_fields(request)
            if not search_fields:
                continue

            qs = model_admin.get_queryset(request)
            qs, use_distinct = model_admin.get_search_results(request, qs, query)
            if use_distinct:
                qs = qs.distinct()

            if not qs.exists():
                continue
            opts = model._meta

            change_url_name = f"admin:{opts.app_label}_{opts.model_name}_change"

            for obj in qs:
                title = opts.object_name
                content = admin_site._get_object_content(obj)
                url = reverse(change_url_name, args=[obj.pk])

                results.append(
                    {
                        "title": title,
                        "content": content,
                        "url": url,
                    }
                )
        return results

    return admin_search_provider


class HyperAdminConfig(AppConfig):
    name = "hyperadmin"

    def ready(self):
        from django.apps import apps
        from django.contrib.admin.sites import AlreadyRegistered
        from .admin import (
            hyperadmin,
            queued_autoreg_sidebar_modules,
            queued_autoreg_apps,
            queued_views,
            queued_actions,
            queued_realms,
        )

        #
        # 1. Autoregister models
        #
        for app_label in queued_autoreg_apps:
            app_config = apps.get_app_config(app_label)
            for model in app_config.get_models():
                try:
                    hyperadmin.register(model)
                except AlreadyRegistered:
                    pass

        # 1. Autoregister sidebar items
        for module in queued_autoreg_sidebar_modules:
            hyperadmin.add_sidebar_modules(module)

        # 2. Extra views (factories)
        for pattern, view_factory, name in queued_views:
            view = view_factory(hyperadmin)
            hyperadmin.register_view(pattern, view, name=name)

        # 3. Actions
        for action, name in queued_actions:
            hyperadmin.add_action(action, name=name)

        # 5. realms
        for realm in queued_realms:
            hyperadmin.add_realm(realm)
        register_global_search_provider(admin_provider_factory(hyperadmin))

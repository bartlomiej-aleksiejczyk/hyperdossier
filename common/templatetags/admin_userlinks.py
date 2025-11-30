from django import template
from django.conf import settings
from django.urls import reverse, NoReverseMatch

register = template.Library()

from django import template
from django.conf import settings
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.simple_tag
def admin_userlinks():
    links = getattr(settings, "ADMIN_CUSTOM_USERLINKS", [])
    resolved = []

    for link in links:
        label = link.get("label")

        if "url" in link:
            resolved.append((label, link["url"]))
            continue

        url_name = link.get("url_name")
        if not url_name:
            continue

        args = link.get("args", [])
        kwargs = link.get("kwargs", {})

        try:
            url = reverse(url_name, args=args, kwargs=kwargs)
            resolved.append((label, url))
        except NoReverseMatch:
            continue
    print(resolved)
    return resolved


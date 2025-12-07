import mimetypes
from pathlib import Path
from django.urls import NoReverseMatch, path, reverse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse
from django.template.response import TemplateResponse
from django.utils.encoding import smart_str
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["GET", "HEAD"])
def protected_media(request, relative_path: str):
    """
    Serve files from MEDIA_ROOT only if the user is logged in.
    Actual bytes are served by Nginx via X-Accel-Redirect.

    URL: /files/<path:relative_path>/
    Example: /files/documents/report.pdf
             -> MEDIA_ROOT/documents/report.pdf
    """
    media_root = Path(settings.MEDIA_ROOT).resolve()
    requested = (media_root / relative_path).resolve()

    try:
        rel_for_internal = requested.relative_to(media_root)
    except ValueError:
        raise Http404("File not found")

    if not requested.is_file():
        raise Http404("File not found")

    content_type, _ = mimetypes.guess_type(requested.name)
    if content_type is None:
        content_type = "application/octet-stream"

    # --- DEV MODE --------------------------------------------------------
    # If running Django dev server, serve file bytes directly
    if settings.DEBUG or getattr(settings, "RUNSERVER", False):
        # HEAD request \u2192 empty body but same headers
        if request.method == "HEAD":
            response = HttpResponse(content_type=content_type)
            response["Content-Length"] = requested.stat().st_size
            response["Content-Disposition"] = (
                f'inline; filename="{smart_str(requested.name)}"'
            )
            return response

        # GET request \u2192 send file bytes
        return FileResponse(
            open(requested, "rb"),
            content_type=content_type,
            as_attachment=False,
            filename=requested.name,
        )

    # --- PROD MODE -------------------------------------------------------
    # Use Nginx X-Accel-Redirect
    internal_path = f"/hyperdossier/protected-media/{rel_for_internal.as_posix()}"

    response = HttpResponse(content_type=content_type)
    response["X-Accel-Redirect"] = internal_path
    response["Content-Disposition"] = f'inline; filename="{smart_str(requested.name)}"'

    response["Cache-Control"] = "private, max-age=3600"

    return response


def health(request):
    return HttpResponse("ok")


def layout_test(request):
    return TemplateResponse(request, "base_layout.html")


def settings_view(request):
    """
    "Settings" page inside admin, using HyperadminSite context.
    """
    try:
        docsroot = reverse("django-admindocs-docroot")
    except NoReverseMatch:
        docsroot = None
    try:
        profile_url = reverse("settings:settings", args=[request.user.pk])
    except NoReverseMatch:
        profile_url = None
    context = dict(
        title=("Settings"),
        docsroot=docsroot,
        profile_url=profile_url,
    )
    return TemplateResponse(
        request,
        "settings.html",
        context,
    )

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from . import views

app_name = "common"

urlpatterns = [
    path("", views.home_index, name="home_index"),
    path(
        "files/<path:relative_path>",
        views.protected_media,
        name="protected_media",
    ),
    path(
        "accounts/login/",
        LoginView.as_view(template_name="security/login.html"),
        name="login",
    ),
    path(
        "accounts/logout/", LogoutView.as_view(next_page="common:login"), name="logout"
    ),
    path("health/", views.health, name="health"),
    path("settings/", views.settings_view, name="settings"),
    path(
    "sitemap.xml",
    sitemap,
    {"sitemaps": sitemaps},
    name="django.contrib.sitemaps.views.sitemap",
)

]

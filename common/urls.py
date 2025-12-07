from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

urlpatterns = [
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
    path("layout-test/", views.layout_test),
]

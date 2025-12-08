from django.urls import path

from . import views

app_name = "infobjects_api"

urlpatterns = [
    path("notes/<int:pk>/", views.NoteDetailViewApi.as_view(), name="note_detail_ajax"),
]

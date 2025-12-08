# notes/urls.py
from django.urls import path
from . import views

app_name = "infobjects"

urlpatterns = [
    # categories
    path("categories/", views.CategoryListCreateView.as_view(), name="category_list"),
    path(
        "categories/<int:pk>/edit/",
        views.CategoryUpdateView.as_view(),
        name="category_edit",
    ),
    path(
        "categories/<int:pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category_delete",
    ),
    # notes
    path("notes/", views.NoteListView.as_view(), name="note_list"),
    path("notes/add/", views.NoteEditView.as_view(), name="note_add"),
    path("notes/<int:pk>/edit/", views.NoteEditView.as_view(), name="note_edit"),
    path("note/<int:pk>/delete/", views.NoteDeleteView.as_view(), name="note_delete"),
    path("notes/<int:pk>/", views.NoteDetailView.as_view(), name="note_detail"),
]

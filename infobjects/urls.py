from django.urls import path
from . import views

app_name = "infobjects"

urlpatterns = [
    path("", views.infobjects_index, name="infobjects_index"),
    path(
        "categories/<int:category_pk>/edit/",
        views.CategoryUpdatePage().as_view(),
        name="category_edit",
    ),
    path(
        "categories/<int:category_pk>/",
        views.CategoryListPage().as_view(),
        name="category_detail",
    ),
    path(
        "categories/<int:category_pk>/delete/",
        views.category_delete,
        name="category_delete",
    ),
    path("categories/", views.CategoryListPage().as_view(), name="category_list"),
    path("categories/new/", views.CategoryCreatePage().as_view(), name="category_new"),
    # notes

    path("notes/", views.NoteListView.as_view(), name="note_list"),
    path("notes/add/", views.NoteEditView.as_view(), name="note_add"),
    path("notes/<int:pk>/edit/", views.NoteEditView.as_view(), name="note_edit"),
    path("note/<int:pk>/delete/", views.NoteDeleteView.as_view(), name="note_delete"),
    path("notes/<int:pk>/", views.NoteDetailView.as_view(), name="note_detail"),
]

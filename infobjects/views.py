import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.template import Template
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from django.views.generic.detail import SingleObjectMixin

from iommi.style_base import base

from infobjects.breadcrumbs import get_breadcrumbs_context

from .models import Category, Note
from .forms import CategoryForm, NoteForm, NoteAttachmentFormSet

from iommi import Action, Column, Header, Page, Form, Table, html


def category_delete(request, category_pk) -> HttpResponseRedirect | HttpResponse:
    category = get_object_or_404(Category, pk=category_pk)
    if request.method == "POST":
        category.delete()
        return redirect("infobjects:category_list")
    return render(request, "category_confirm_delete.html", {"category": category})


def note_delete(request, pk) -> HttpResponseRedirect | HttpResponse:
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        note.delete()
        return redirect("infobjects:note_list")
    return render(request, "note_confirm_delete.html", {"note": note})


def infobjects_index(request) -> HttpResponse:
    return render(request, "infobjects/infobjects_index.html")


class CategoryCreatePage(Page):
    create = Form.create(
        title="Create a new category",
        auto__model=Category,
        auto__include=["title"],
        actions__submit__display_name="Add",
        extra__redirect_to=reverse_lazy("infobjects:category_list"),
    )

    class Meta:
        iommi_style = "infobjects_style"
        context__breadcrumbs = lambda request, **_: get_breadcrumbs_context(
            "infobjects:category_new", {}
        )["breadcrumbs"]


class CategoryListPage(Page):
    list = Table(
        auto__model=Category,
        title="Available Categories",
        columns__edit=Column.edit(
            after=0, include=lambda request, **_: request.user.is_staff
        ),
        attrs__class={"table-stretched": True},
        columns__delete=Column.delete(
            cell__template=Template(
                '<td data-iommi-path="parts__list__columns__delete__cell" data-iommi-type="Cell" style="">'
                '<form action="{% url "infobjects:category_delete" row.pk %}" method="post" onsubmit="return confirm(\'Are you sure to remove a category named {{row.title}}?\');" class="hidden-form">'
                "{% csrf_token %}"
                '<button type="submit" class="text-danger">'
                '<i class="fa fa-lg fa-trash-o"></i> Delete'
                "</button>"
                "</form>"
                "</td>"
            ),
            include=lambda request, **_: request.user.is_staff,
        ),
        outer__children__figure_close=html.figure(),
        container__tag="figure",
    )

    class Meta:
        iommi_style = "infobjects_style"
        context__breadcrumbs = lambda **_: get_breadcrumbs_context(
            "infobjects:category_list", {}
        )["breadcrumbs"]


class CategoryUpdatePage(Page):
    create = Form.edit(
        actions__cancel=Action(attrs__href="../"),
        auto__model=Category,
        auto__include=["title"],
        actions__submit__display_name="Add",
        instance=lambda category_pk, **kwargs: Category.objects.filter(
            pk=category_pk
        ).first(),
        extra__redirect_to=reverse_lazy("infobjects:category_list"),
    )

    class Meta:
        iommi_style = "infobjects_style"
        context__breadcrumbs = (
            lambda request, category_pk, **_: get_breadcrumbs_context(
                "infobjects:category_edit", {"category_pk": category_pk}
            )["breadcrumbs"]
        )


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "infobjects/category_form.html"
    success_url = reverse_lazy("infobjects:category_list")


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = "infobjects/category_confirm_delete.html"
    success_url = reverse_lazy("infobjects:category_list")


def map_notes_to_menu_items(notes):
    """
    Convert a list/queryset of Note objects into sidebar menu items format.

    Expected output structure:

    [
        {"label": ..., "url": ..., "children": []},
        ...
    ]
    """

    items = []

    for note in notes:
        items.append(
            {
                "label": note.title,
                "url": note.get_absolute_url(),
                "children": [],
            }
        )

    return items


def note_list(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "sidebar/menu_items.html",
            get_sidebar_context(request),
            request=request,
        )

        return HttpResponse(html)
    notes = Note.objects.select_related("category").all()

    category_id = request.GET.get("category")
    if category_id:
        notes = notes.filter(category_id=category_id)

    context = {
        "notes": notes,
    }
    return render(request, "infobjects/note_list.html", context)


def note_editor(request):
    context = get_sidebar_context(request)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "sidebar/menu_items.html",
            context,
            request=request,
        )
        return HttpResponse(html)
    return render(request, "infobjects/note_detail.html", context)


class NoteCreateEditView(View):
    """
    Create or edit a Note with inline attachments (no autosave here).
    Uses NoteForm + NoteAttachmentFormSet, similar to Django admin inlines.
    """

    template_name = "infobjects/note_form.html"
    form_class = NoteForm
    formset_class = NoteAttachmentFormSet

    def get_object(self):
        pk = self.kwargs.get("pk")
        if pk is not None:
            return get_object_or_404(Note, pk=pk)
        return None

    def get(self, request, *args, **kwargs):

        note = self.get_object()
        form = self.form_class(instance=note)
        formset = self.formset_class(instance=note)
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "formset": formset,
                "note": note,
                **get_sidebar_context(request),
            },
        )

    def post(self, request, *args, **kwargs):
        note = self.get_object()
        form = self.form_class(request.POST, instance=note)
        formset = self.formset_class(
            request.POST,
            request.FILES,
            instance=note,
        )

        if form.is_valid() and formset.is_valid():
            note = form.save()
            formset.instance = note
            formset.save()
            return redirect("infobjects:note_detail", pk=note.pk)

        return render(
            request,
            self.template_name,
            {"form": form, "formset": formset, "note": note},
        )


def get_sidebar_context(request, **kwargs):
    context = {}

    category_id = request.GET.get("category", "")

    context["categories"] = Category.objects.order_by("title")
    context["selected_category"] = category_id

    if category_id:
        notes = Note.objects.filter(Q(category_id=category_id)).select_related(
            "category"
        )
    else:
        notes = Note.objects.select_related("category")

    context["menu_items"] = map_notes_to_menu_items(notes)

    return context


class NoteDetailView(LoginRequiredMixin, DetailView):
    model = Note
    template_name = "infobjects/note_detail.html"
    context_object_name = "note"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_sidebar_context(self.request))

        return context


class NoteDetailViewApi(LoginRequiredMixin, SingleObjectMixin, View):
    """
    JSON endpoint for auto-update (AJAX/htmx).
    Returns:
    {
      "status": "ok",
      "result": {
        "note_content": "...",
        "note_title": "...",
        "note_type": "PLAINTEXT"
      }
    }
    """

    model = Note
    context_object_name = "note"

    def get(self, request, pk, *args, **kwargs):
        note = get_object_or_404(Note, pk=pk)

        # Map your internal type to whatever string you want to expose
        # Here I just pass the raw DB value; you can adjust if needed.
        # Example mapping if you want PLAINTEXT instead of TEXT:
        type_mapping = {
            Note.NoteType.TEXT: "PLAINTEXT",
            Note.NoteType.TODO: "TODO",
            Note.NoteType.JSON: "JSON",
        }
        attachments = [
            {
                "id": att.id,
                "name": att.file.name,
                "url": att.file.url,
                "size": att.file.size,
                "uploaded": att.uploaded_at.isoformat(),
            }
            for att in note.attachments.all()
        ]

        payload = {
            "status": "ok",
            "result": {
                "note_content": note.content,
                "note_title": note.title,
                "note_type": type_mapping.get(note.type, note.type),
                "note_attachments": attachments,
                "note_updated_at": note.updated_at,
            },
        }
        return JsonResponse(payload)

    def post(self, request, *args, **kwargs):
        note = self.get_object()

        try:
            data = json.loads(request.body.decode("utf-8"))
        except (ValueError, TypeError):
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON payload"},
                status=400,
            )

        content = data.get("content")
        title = data.get("note_title") or data.get("title")  # support both keys

        changed_fields = []

        if content is not None and content != note.content:
            note.content = content
            changed_fields.append("content")

        if title is not None and title != note.title:
            note.title = title
            changed_fields.append("title")

        if changed_fields:
            note.save(update_fields=changed_fields + ["updated_at"])

        return JsonResponse({"status": "ok", "updated_at": note.updated_at.isoformat()})


class NoteDeleteView(DeleteView):
    model = Note
    template_name = "infobjects/note_confirm_delete.html"
    success_url = reverse_lazy("infobjects:note_list")


class NoteListPage(Page):
    list = Table(
        auto__model=Note,
        auto__exclude=["content"],
        columns__edit=Column.edit(after=0),
        attrs__class={"table-stretched": True},
        columns__delete=Column.delete(
            cell__template=Template(
                '<td data-iommi-path="parts__list__columns__delete__cell" data-iommi-type="Cell" style="">'
                '<form action="{% url "infobjects:note_delete" row.pk %}" method="post" onsubmit="return confirm(\'Are you sure to remove a note named {{row.title}}?\');" class="hidden-form">'
                "{% csrf_token %}"
                '<button type="submit" class="text-danger">'
                '<i class="fa fa-lg fa-trash-o"></i> Delete'
                "</button>"
                "</form>"
                "</td>"
            ),
            include=lambda request, **_: request.user.is_staff,
        ),
        outer__children__figure_close=html.figure(),
        container__tag="figure",
    )

    class Meta:
        iommi_style = "infobjects_style"
        context__breadcrumbs = lambda request, **_: get_breadcrumbs_context(
            "infobjects:notel_list", {}
        )["breadcrumbs"]

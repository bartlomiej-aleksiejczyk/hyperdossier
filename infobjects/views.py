import json

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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.detail import SingleObjectMixin

from .models import Category, Note
from .forms import CategoryForm, NoteForm, NoteForm, NoteAttachmentFormSet


class CategoryListCreateView(LoginRequiredMixin, ListView, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "infobjects/category_list.html"
    context_object_name = "categories"
    success_url = reverse_lazy("infobjects:category_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # For ListView part, object_list is categories
        context.setdefault("form", self.get_form())
        return context


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "infobjects/category_form.html"
    success_url = reverse_lazy("infobjects:category_list")


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = "infobjects/category_confirm_delete.html"
    success_url = reverse_lazy("infobjects:category_list")


from django.shortcuts import get_object_or_404


class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = "infobjects/note_list.html"
    context_object_name = "notes"

    def get_queryset(self):
        qs = super().get_queryset()
        category_id = self.request.GET.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs.select_related("category")


class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = "infobjects/note_form.html"

    def get_success_url(self):
        return reverse_lazy("infobjects:note_edit", args=[self.object.pk])


class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = "infobjects/note_form.html"

    def get_success_url(self):
        return reverse_lazy("infobjects:note_edit", args=[self.object.pk])


class NoteEditView(LoginRequiredMixin, View):
    """
    Create or edit a Note with inline attachments (no autosave here).
    Uses NoteForm + NoteAttachmentFormSet, similar to Django admin inlines.
    """

    template_name = "infobjects/note_edit.html"
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
            {"form": form, "formset": formset, "note": note},
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


class NoteDetailView(LoginRequiredMixin, DetailView):
    model = Note
    template_name = "infobjects/note_detail.html"
    context_object_name = "note"


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


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    template_name = "infobjects/note_confirm_delete.html"
    success_url = reverse_lazy("infobjects:note_list")

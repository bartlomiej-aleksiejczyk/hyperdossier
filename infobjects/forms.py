from django import forms
from .models import Category, Note, NoteAttachment
from django.forms import inlineformset_factory


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["title"]


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "type", "content", "category"]


class NoteAttachmentForm(forms.ModelForm):
    class Meta:
        model = NoteAttachment
        fields = ["file", "original_name", "mime_type"]


NoteAttachmentFormSet = inlineformset_factory(
    Note,
    NoteAttachment,
    form=NoteAttachmentForm,
    extra=1,
    can_delete=True,
)

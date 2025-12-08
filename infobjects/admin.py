from django.contrib import admin
from hyperadmin.admin import hyperadmin
from .models import Note, NoteAttachment


class NoteAttachmentInline(admin.TabularInline):
    model = NoteAttachment
    extra = 1
    fields = ("file", "original_name", "mime_type")
    readonly_fields = ("uploaded_at",)


class InfobjectAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "short_content", "created_at", "updated_at")
    inlines = [NoteAttachmentInline]

    def short_content(self, obj):
        return (obj.content[:60] + "…") if len(obj.content) > 60 else obj.content

    short_content.short_description = "Content"


hyperadmin.register(Note, InfobjectAdmin)

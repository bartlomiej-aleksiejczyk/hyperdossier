from django.db import models


class Category(models.Model):
    """
    A simple Category model (not nested).
    """

    title = models.CharField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Note(models.Model):
    class Meta:
        ordering = ["-updated_at"]

    class NoteType(models.TextChoices):
        TEXT = "TEXT", "Text"
        TODO = "TODO", "Todo"
        JSON = "JSON", "JSON"

    type = models.CharField(
        max_length=10,
        choices=NoteType.choices,
        default=NoteType.TEXT,
    )
    title = models.CharField(max_length=255)
    content = models.TextField(
        help_text="Text body or JSON string, depending on the type."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notes",
    )

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"


class NoteAttachment(models.Model):
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(upload_to="notes/attachments/%Y/%m/%d/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_name = models.CharField(max_length=255, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.original_name:
            self.original_name = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.original_name or self.file.name

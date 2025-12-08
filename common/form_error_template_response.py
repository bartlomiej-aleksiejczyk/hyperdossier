from django.template.response import TemplateResponse


class FormErrorTemplateResponse(TemplateResponse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if any(
            getattr(form, "errors", False)
            for form in self.context_data.values()
            if hasattr(form, "errors")
        ):
            self.status_code = 422
            self["X-Form-Status"] = "failed"

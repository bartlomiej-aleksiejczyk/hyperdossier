from hyperadmin.admin import hyperadmin
from django.contrib.auth.admin import UserAdmin
from .models import CustomizedUser, FailedLogin


hyperadmin.register(CustomizedUser, UserAdmin)
hyperadmin.register(FailedLogin)

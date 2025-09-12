

# Register your models here.
from django.contrib import admin
from .models import Device, ChangeLog

admin.site.register(Device)
admin.site.register(ChangeLog)



# Register your models here.
from django.contrib import admin
from .models import PointsTransaction, Progress, Badge, UserBadge

admin.site.register(PointsTransaction)
admin.site.register(Progress)
admin.site.register(Badge)
admin.site.register(UserBadge)

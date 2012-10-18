from datetime import datetime


def make_approved(modeladmin, request, queryset):
    queryset.update(approved=datetime.now())

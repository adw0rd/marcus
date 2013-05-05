from datetime import datetime


def make_approved(modeladmin, request, queryset):
    for item in queryset:
        item.approved = datetime.now()
        item.save()

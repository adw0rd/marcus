from datetime import datetime

from django.utils.translation import ugettext as _


def make_approved(modeladmin, request, queryset):
    for item in queryset:
        item.approved = datetime.now()
        item.save()
make_approved.allow_tags = True
make_approved.short_description = _("Make approved")

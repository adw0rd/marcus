from django.utils.translation import ugettext as _
from django.utils import timezone


def make_approved(modeladmin, request, queryset):
    for item in queryset:
        item.approved = timezone.now()
        item.save()
make_approved.allow_tags = True
make_approved.short_description = _("Make approved")

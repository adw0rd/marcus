from django.db import models
from django.apps import apps
from django.conf import settings

MARCUS_SEARCH_FIELDS = ['title_ru', 'title_en', 'text_ru', 'text_en', ]
if hasattr(settings, 'MARCUS_SEARCH_FIELDS'):
    MARCUS_SEARCH_FIELDS = settings.MARCUS_SEARCH_FIELDS


class MarcusQuerySet(models.query.QuerySet):
    """Substitution the QuerySet
    """
    search_fields = MARCUS_SEARCH_FIELDS

    def search(self, search_query):
        if search_query:
            qq = models.Q()
            for field in self.search_fields:
                qq |= models.Q(**{"{0}__icontains".format(field): search_query})
            return self.filter(qq).distinct()
        return self.filter(pk__isnull=True)


class MarcusManager(models.Manager):
    def get_queryset(self):
        model = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        return MarcusQuerySet(model)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_queryset(), attr, *args)

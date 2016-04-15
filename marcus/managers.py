from django.db import models
from django.conf import settings

from marcus.queryset import MarcusManager


class CommonLanguageManager(MarcusManager):

    def language(self, code):
        queryset = self.get_queryset()
        if code == 'en':
            queryset = queryset.exclude(title_en='')
        elif code == 'ru':
            queryset = queryset.exclude(title_ru='')
        return queryset


class PublicArticlesManager(CommonLanguageManager):
    def get_queryset(self):
        return super(PublicArticlesManager, self).get_queryset()\
            .exclude(published=None).order_by('-published')


class CategoryManager(CommonLanguageManager):
    def language(self, code):
        queryset = super(CategoryManager, self).language(code)
        queryset = queryset.order_by('title_en' if code == 'en' else 'title_ru')
        return queryset

    def popular(self, code):
        order_by = ['-essential']
        queryset = self.get_queryset()
        if code == "en":
            order_by.append('-count_articles_en')
            queryset = queryset.filter(count_articles_en__gt=0)
        else:
            order_by.extend(['-count_articles_ru', '-count_articles_en', ])
            queryset = queryset.filter(models.Q(count_articles_ru__gt=0) | models.Q(count_articles_en__gt=0))
        return queryset.order_by(*order_by)


class TagManager(CategoryManager):
    def popular(self, code):
        order_by = []
        queryset = self.get_queryset()
        if code == "en":
            order_by.append('-count_articles_en')
            queryset = queryset.filter(count_articles_en__gt=0)
        else:
            order_by.extend(['-count_articles_ru', '-count_articles_en', ])
            queryset = queryset.filter(
                models.Q(count_articles_ru__gt=settings.MARCUS_TAG_MINIMUM_ARTICLES) |
                models.Q(count_articles_en__gt=settings.MARCUS_TAG_MINIMUM_ARTICLES))
        return queryset.order_by(*order_by)


class CommentsManager(models.Manager):
    def language(self, code):
        queryset = self.get_queryset()
        if code:
            queryset = queryset.filter(language=code)
        return queryset


class PublicCommentsManager(CommentsManager):
    def get_queryset(self):
        return super(PublicCommentsManager, self).get_queryset()\
            .exclude(approved=None).order_by('created')


class SuspectedCommentsManager(models.Manager):
    def get_queryset(self):
        return super(SuspectedCommentsManager, self).get_queryset()\
            .filter(approved=None).exclude(spam_status='clean')\
            .order_by('-created')

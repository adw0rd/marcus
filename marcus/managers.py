# coding: utf-8
from django.db import models


class CommonLanguageManager(models.Manager):
    def language(self, code):
        qs = self.get_query_set()
        if code == 'en':
            qs = qs.exclude(text_en='')
        elif code == 'ru':
            qs = qs.exclude(text_ru='')
        return qs


class PublicArticlesManager(CommonLanguageManager):
    def get_query_set(self):
        return super(PublicArticlesManager, self).get_query_set()\
            .exclude(published=None).order_by('-published')


class CategoryManager(CommonLanguageManager):
    def language(self, code):
        qs = super(CategoryManager, self).language(code)
        qs = qs.order_by('title_en' if code == 'en' else 'title_ru')
        return qs


class TagManager(CommonLanguageManager):
    pass


class CommentsManager(models.Manager):
    def language(self, code):
        qs = self.get_query_set()
        if code:
            qs = qs.filter(language=code)
        return qs


class PublicCommentsManager(CommentsManager):
    def get_query_set(self):
        return super(PublicCommentsManager, self).get_query_set()\
            .exclude(approved=None).order_by('created')


class SuspectedCommentsManager(models.Manager):
    def get_query_set(self):
        return super(SuspectedCommentsManager, self).get_query_set()\
            .filter(approved=None).exclude(spam_status='clean')\
            .order_by('-created')

# coding: utf-8
import re
import pytils
import markdown2
import smorg_style.utils
import pingdjack
import subhub
from datetime import datetime
from scipio.models import Profile

from django.db import models
from django.db import transaction
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words
from django.utils.html import strip_tags
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _

from marcus import utils
from marcus import managers


class Translation(object):
    def __init__(self, obj, language):
        super(Translation, self).__init__()
        self.obj = obj
        self.language = language

    def __getattr__(self, name):
        attr = getattr(self.obj, name)
        if getattr(attr, 'needs_language', None):
            attr = curry(attr, self.language)
        return attr

    def __dir__(self):
        return dir(self.obj)


class Category(models.Model):
    slug = models.SlugField(unique=True, blank=True)
    title_ru = models.CharField(max_length=255, blank=True)
    description_ru = models.TextField(blank=True)
    title_en = models.CharField(max_length=255, blank=True)
    description_en = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    essential = models.BooleanField(default=False, db_index=True)

    objects = managers.CategoryManager()

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __unicode__(self):
        return self.title()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = pytils.translit.slugify(self.title_ru or self.title_en)
        return self.save_base(*args, **kwargs)

    def title(self, language=None):
        if language:
            return self.title_en if language == 'en' else self.title_ru
        else:
            return self.title_ru or self.title_en
    title.needs_language = True

    def description(self, language=None):
        if language:
            return self.description_en if language == 'en' else self.description_ru
        else:
            return self.description_ru or self.description_en
    description.needs_language = True

    def get_absolute_url(self, language=None):
        return utils.iurl(reverse('marcus-category', args=[self.slug]), language)
    get_absolute_url.needs_language = True

    def get_feed_url(self, language=None):
        return utils.iurl('%sfeed/' % self.get_absolute_url(), language)
    get_feed_url.needs_language = True

    def article_count(self, language=None):
        return Article.public.language(language).filter(categories=self).count()
    article_count.needs_language = True


class Tag(models.Model):
    slug = models.SlugField(unique=True, blank=True)
    title_ru = models.CharField(max_length=255, blank=True)
    description_ru = models.TextField(blank=True)
    title_en = models.CharField(max_length=255, blank=True)
    description_en = models.TextField(blank=True)

    def __unicode__(self):
        return self.title()

    def title(self, language=None):
        if language:
            return self.title_en if language == 'en' else self.title_ru
        else:
            return self.title_ru or self.title_en
    title.needs_language = True


class Article(models.Model):
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    title_ru = models.CharField(max_length=255, blank=True)
    text_ru = models.TextField(blank=True)
    title_en = models.CharField(max_length=255, blank=True)
    text_en = models.TextField(blank=True)
    published = models.DateTimeField(blank=True, null=True, db_index=True)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    updated = models.DateTimeField(auto_now=True)
    comments_hidden = models.BooleanField(default=False)

    objects = models.Manager()
    public = managers.PublicArticlesManager()

    def __unicode__(self):
        return self.slug

    def _notify_hub(self):
        def languages():
            if self.text_ru:
                yield 'ru'
            if self.text_en:
                yield 'en'
            if self.text_ru and self.text_en:
                yield None

        for language in languages():
            topics = [utils.iurl(reverse('marcus-feed'), language)] + \
                     [c.get_feed_url(language) for c in self.categories.all()]
            subhub.publish(
                [utils.absolute_url(t) for t in topics],
                utils.absolute_url(self.get_absolute_url(language)),
            )

    def _pingback(self):
        if settings.DEBUG:
            return None
        language = 'en' if self.text_en else None
        pingdjack.ping_external_urls(
            utils.absolute_url(self.get_absolute_url(language)),
            self.html(language),
            utils.absolute_url(utils.iurl(reverse('marcus-index'), language))
        )

    def save(self, **kwargs):
        if not self.slug:
            self.slug = pytils.translit.slugify(self.title_ru or self.title_en)
        already_published = bool(Article.objects.filter(pk=self.pk).exclude(published=None))
        super(Article, self).save(**kwargs)
        if self.published:
            if transaction.is_managed():
                transaction.commit()
            if not already_published:
                self._pingback()
            self._notify_hub()

    def only_language(self):
        return None if (self.text_en and self.text_ru) else 'en' if self.text_en else 'ru'

    def is_bilingual(self):
        return not self.only_language()

    def comment_language(self, display_language):
        if self.is_bilingual():
            return display_language or 'ru'
        return 'en' if self.text_en else 'ru'

    def get_absolute_url(self, language=None):
        if self.published:
            url = reverse('marcus-article', args=[
                '%04d' % self.published.year,
                '%02d' % self.published.month,
                '%02d' % self.published.day,
                self.slug
            ])
        else:
            url = reverse('marcus-draft', args=[self.pk])
        return utils.iurl(url, language)
    get_absolute_url.needs_language = True

    def get_translation_url(self, language=None):
        return self.get_absolute_url(utils.altlanguage(language))
    get_translation_url.needs_language = True

    def get_feed_url(self, language=None):
        return utils.iurl('%sfeed/' % self.get_absolute_url(), language)
    get_feed_url.needs_language = True

    def title(self, language=None):
        if language:
            return self.title_en if language == 'en' else self.title_ru
        else:
            return self.title_ru or self.title_en
    title.needs_language = True

    def _language_text(self, language):
        if language:
            return self.text_en if language == 'en' else self.text_ru
        else:
            return self.text_ru or self.text_en

    def html(self, language=None):
        html = markdown2.markdown(self._language_text(language))
        html = smorg_style.utils.usertext(html)
        return mark_safe(html)
    html.needs_language = True

    def summary(self, language=None):
        return mark_safe(truncate_words(strip_tags(self.html(language)), 50))
    summary.needs_language = True

    def intro(self, language=None):
        result = markdown2.markdown(self._language_text(language))
        pattern = re.compile(r'^(.*)<a name="more"></a>.*', re.S)
        match = re.match(pattern, result)
        return match and mark_safe(match.group(1))
    intro.needs_language = True

COMMENT_TYPES = (
    ('comment', u'Комментарий'),
    ('pingback', u'Pingback'),
)

LANGUAGES = (
    ('ru', _(u'Russian')),
    ('en', _(u'English')),
)


class ArticleUpload(models.Model):
    article = models.ForeignKey(Article, related_name="uploads")
    upload = models.FileField(upload_to="uploads")

    def __unicode__(self):
        return self.upload.name


class Comment(models.Model):
    article = models.ForeignKey(Article)
    type = models.CharField(max_length=20, choices=COMMENT_TYPES)
    text = models.TextField(_(u'Text'))
    language = models.CharField(_(u'Language'), max_length=2, choices=LANGUAGES)
    author = models.ForeignKey(User)
    guest_name = models.CharField(max_length=255, blank=True)
    guest_email = models.CharField(max_length=200, blank=True, default='')
    guest_url = models.URLField(blank=True)
    ip = models.IPAddressField(default='127.0.0.1')
    spam_status = models.CharField(max_length=20, blank=True, default='')
    created = models.DateTimeField(default=datetime.now, db_index=True)
    approved = models.DateTimeField(null=True, blank=True, db_index=True)
    noteworthy = models.BooleanField(default=False)

    objects = models.Manager()
    public = managers.PublicCommentsManager()
    suspected = managers.SuspectedCommentsManager()
    common = managers.CommentsManager()

    def __unicode__(self):
        return u'%s, %s, %s' % (self.created.strftime('%Y-%m-%d'), self.article, self.author_str())

    def get_absolute_url(self, language=None):
        article = Translation(self.article, language)
        return '%s#comment-%s' % (article.get_absolute_url(), self.pk)
    get_absolute_url.needs_language = True

    def html(self):
        html = smorg_style.utils.usertext(markdown2.markdown(self.text))
        return mark_safe(html)

    def summary(self):
        return mark_safe(truncate_words(strip_tags(self.html()), 50))

    def by_guest(self):
        return self.author.username == 'marcus_guest'

    def author_str(self):
        if self.by_guest():
            return self.guest_name
        try:
            return unicode(self.author.scipio_profile)
        except Profile.DoesNotExist:
            return unicode(self.author)

    def author_url(self):
        try:
            return self.author.scipio_profile.openid
        except (Profile.DoesNotExist, AttributeError):
            return None

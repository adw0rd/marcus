import re
import hashlib
import pytils
import markdown2
import pingdjack
import itertools

from scipio.models import Profile

from django.db import models
from django.db import transaction
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django.utils.html import strip_tags
from django.utils.functional import curry
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save

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

    def __unicode__(self):
        """For drawing sequence

        Example:
        {% with article|translate:language as article %}
            Tags: {{ article.tags_links|safeseq|join:", " }}
        {% endwith %}
        """
        return unicode(self.obj)


class Category(models.Model):
    slug = models.SlugField(unique=True, blank=True)
    title_ru = models.CharField(max_length=255, blank=True)
    description_ru = models.TextField(blank=True)
    count_articles_ru = models.PositiveIntegerField(default=0)
    title_en = models.CharField(max_length=255, blank=True)
    description_en = models.TextField(blank=True)
    count_articles_en = models.PositiveIntegerField(default=0)
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
            self.slug = pytils.translit.slugify(self.title_en or self.title_ru)
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

    def anchor(self, language=None):
        return u'<a href="{0}">{1}</a>'.format(self.get_absolute_url(language), self.title(language))
    anchor.needs_language = True


class Tag(models.Model):
    slug = models.SlugField(unique=True, blank=True)
    title_ru = models.CharField(max_length=255, blank=True)
    description_ru = models.TextField(blank=True)
    count_articles_ru = models.PositiveIntegerField(default=0)
    title_en = models.CharField(max_length=255, blank=True)
    description_en = models.TextField(blank=True)
    count_articles_en = models.PositiveIntegerField(default=0)

    objects = managers.TagManager()

    def __unicode__(self):
        return self.title()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = pytils.translit.slugify(self.title_en or self.title_ru)

        if not self.title_en and utils.get_language_code_in_text(self.title_ru) == "en":
            self.title_en = self.title_ru

        if not self.title_ru:
            self.title_ru = self.title_en

        return self.save_base(*args, **kwargs)

    def get_absolute_url(self, language=None):
        return utils.iurl(reverse('marcus-tag', args=[self.slug]), language)
    get_absolute_url.needs_language = True

    def title(self, language=None):
        if language:
            return self.title_en if language == 'en' else self.title_ru
        else:
            return self.title_ru or self.title_en
    title.needs_language = True

    def article_count(self, language=None):
        return Article.public.language(language).filter(tags=self).count()
    article_count.needs_language = True

    def anchor(self, language=None):
        return u'<a href="{0}">{1}</a>'.format(self.get_absolute_url(language), self.title(language))
    anchor.needs_language = True

    def count(self, language=None):
        if language:
            count = self.count_articles_en if language == 'en' else self.count_articles_ru
        else:
            count = self.count_articles_ru or self.count_articles_en
        return count
    count.needs_language = True

    def size(self, language=None):
        return "{0}%".format(100 + (self.count(language) * 3))
    size.needs_language = True

    def css_class(self):
        return "tag_item"


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
            if not transaction.get_autocommit():
                transaction.commit()
            if not already_published:
                self._pingback()

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

    def get_admin_url(self):
        viewname = "admin:{0}_{1}_change".format(
            self._meta.app_label,
            self._meta.model_name)
        return reverse(viewname, args=(self.pk, ))

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
        html = markdown2.markdown(self._language_text(language), extras=settings.MARCUS_MARKDOWN_EXTRAS)
        return mark_safe(html)
    html.needs_language = True

    def summary(self, language=None):
        return mark_safe(Truncator(strip_tags(self.html(language))).words(50))
    summary.needs_language = True

    def intro(self, language=None):
        result = markdown2.markdown(self._language_text(language), extras=settings.MARCUS_MARKDOWN_EXTRAS)
        pattern = re.compile(r'^(.*)<a name="more"></a>.*', re.S)
        match = re.match(pattern, result)
        return match and mark_safe(match.group(1))
    intro.needs_language = True

    def link(self, language=None):
        return u'<a href="{url}">{title}</a>'.format(
            url=self.get_absolute_url(language),
            title=self.title(language)
        )
    html.needs_language = True

    def full_link(self, language=None):
        current_site = Site.objects.get_current()
        url = "http://{domain}{url}".format(domain=current_site.domain, url=self.get_absolute_url(language))
        return u'<a href="{url}">{title}</a>'.format(url=url, title=self.title(language))
    html.needs_language = True

    def categories_links(self, language=None):
        return [category.anchor(language) for category in self.categories.all()]
    categories_links.needs_language = True

    def tags_links(self, language=None):
        return [tag.anchor(language) for tag in self.tags.all()]
    tags_links.needs_language = True

COMMENT_TYPES = (
    ('comment', _('Comment')),
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
    article = models.ForeignKey(Article, related_name='comments')
    type = models.CharField(max_length=20, choices=COMMENT_TYPES)
    text = models.TextField(_(u'Text'))
    language = models.CharField(_(u'Language'), max_length=2, choices=LANGUAGES)
    author = models.ForeignKey(User)
    guest_name = models.CharField(max_length=255, blank=True)
    guest_email = models.CharField(max_length=200, blank=True, default='')
    guest_url = models.URLField(blank=True)
    ip = models.GenericIPAddressField(default='127.0.0.1')
    spam_status = models.CharField(max_length=20, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    approved = models.DateTimeField(null=True, blank=True, db_index=True)
    noteworthy = models.BooleanField(default=False)
    followup = models.BooleanField(
        help_text=_("Receive by email further comments in this conversation"),
        default=False, blank=True)

    objects = models.Manager()
    public = managers.PublicCommentsManager()
    suspected = managers.SuspectedCommentsManager()
    common = managers.CommentsManager()

    def make_token(self, salt="something"):
        secrets = map(unicode, [self.pk, self.guest_email, self.created, self.ip, salt])
        return hashlib.md5(u":".join(secrets)).hexdigest()

    def __unicode__(self):
        return u'%s, %s, %s' % (self.created.strftime('%Y-%m-%d'), self.article, self.author_str())

    def get_absolute_url(self, language=None):
        article = Translation(self.article, language)
        return '%s#comment-%s' % (article.get_absolute_url(), self.pk)
    get_absolute_url.needs_language = True

    def get_admin_url(self):
        viewname = "admin:{0}_{1}_change".format(
            self._meta.app_label,
            self._meta.model_name)
        return reverse(viewname, args=(self.pk, ))

    def html(self):
        html = markdown2.markdown(self.text, extras=settings.MARCUS_MARKDOWN_EXTRAS)
        return mark_safe(html)

    def summary(self):
        return mark_safe(Truncator(strip_tags(self.html())).words(50))

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


def update_tag_and_category_counts(sender, instance, created, **kwargs):
    """Recalculation a counts for articles
    """
    objects = itertools.chain(instance.tags.all(), instance.categories.all())
    for o in objects:
        if instance.text_en:
            o.count_articles_en = o.article_count(language="en")
        if instance.text_ru:
            o.count_articles_ru = o.article_count(language="ru")
        o.save()
post_save.connect(update_tag_and_category_counts, sender=Article)


def notify_followers(sender, instance, created, **kwargs):
    if instance.approved:
        utils.notify_comment_followers(instance)
    if not instance.spam_status:
        utils.notify_comment_managers(instance)
post_save.connect(notify_followers, sender=Comment)

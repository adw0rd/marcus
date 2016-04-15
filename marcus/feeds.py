# coding: utf-8
from hashlib import md5

from django.core.urlresolvers import reverse
from django.template import loader, Template, Context, TemplateDoesNotExist
from django.views.decorators.http import condition
from django.contrib.syndication import views
from django.contrib.auth.models import User
from django.utils.feedgenerator import Atom1Feed
from django.utils import translation
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.conf import settings

from marcus import models, utils


class ContentAtom1Feed(Atom1Feed):
    def add_root_elements(self, handler):
        super(ContentAtom1Feed, self).add_root_elements(handler)
        hub_link = self.feed.get('hub_link')
        if hub_link is not None:
            handler.addQuickElement(u'link', '', {
                u'rel': u'hub',
                u'href': hub_link,
            })
        image_url = getattr(settings, 'MARCUS_FEED_IMAGE', '')
        handler.addQuickElement(u'logo', image_url, {})

    def add_item_elements(self, handler, item):
        super(ContentAtom1Feed, self).add_item_elements(handler, item)
        if item['content'] is not None:
            handler.addQuickElement(u'content', item['content'], {u'type': u'html', u'xml:base': item['link']})


def viewmethod(view):
    def method(self, request, *args, **kwargs):
        return view(request, self, *args, **kwargs)
    return method


class ContentFeed(views.Feed):
    feed_type = ContentAtom1Feed
    content_template = ''

    def hub_link(self, obj):
        pass

    def feed_extra_kwargs(self, obj):
        return {
            'hub_link': utils.absolute_url(self.hub_link(obj)),
        }

    def item_extra_kwargs(self, item):
        try:
            template = loader.get_template(self.content_template)
        except TemplateDoesNotExist:
            template = Template('{{ obj }}')
        return {
            'content': template.render(Context({'obj': item})),
        }

    def etag(self, request, *args, **kwargs):
        obj, language = self.get_object(request, *args, **kwargs)
        qs = self.get_queryset(obj, language)
        if not qs:
            return None
        return md5(str((self.updated(qs[0]), language))).hexdigest()

    @viewmethod
    @condition(lambda r, s, *args, **kwargs: s.etag(r, *args, **kwargs))
    def __call__(request, self, *args, **kwargs):
        return super(ContentFeed, self).__call__(request, *args, **kwargs)


class ArticleFeed(object):
    title_template = 'marcus/feeds/article_title.html'
    description_template = 'marcus/feeds/article_summary.html'
    content_template = 'marcus/feeds/article_content.html'
    author = User.objects.get(pk=settings.MARCUS_AUTHOR_ID)
    title = settings.MARCUS_TITLE
    subtitle = settings.MARCUS_SUBTITLE

    def author_name(self):
        return self.author.scipio_profile

    def items(self, (obj, language)):
        qs = self.get_queryset(obj, language)[:settings.MARCUS_ITEMS_IN_FEED]
        return [models.Translation(a, language) for a in qs]

    def item_pubdate(self, article):
        return article.published

    def updated(self, article):
        return article.published


class Article(ArticleFeed, ContentFeed):
    def get_object(self, request, language):
        translation.activate(language or 'ru')
        return None, language

    def link(self, (obj, language)):
        return utils.iurl(reverse('marcus-index'), language)

    def get_queryset(self, obj, language):
        return models.Article.public.language(language)


class Category(ArticleFeed, ContentFeed):
    def get_object(self, request, slug, language):
        translation.activate(language or 'ru')
        category = get_object_or_404(models.Category, slug=slug)
        return category, language

    def title(self, (category, language)):
        category = models.Translation(category, language)
        return u'%s » %s' % (settings.MARCUS_TITLE, category.title())

    def link(self, (category, language)):
        return utils.iurl(reverse('marcus-category', args=[category.slug]), language)

    def get_queryset(self, category, language):
        return models.Article.public.language(language).filter(categories=category)


class Tag(ArticleFeed, ContentFeed):
    def get_object(self, request, slug, language):
        translation.activate(language or 'ru')
        tag = get_object_or_404(models.Tag, slug=slug)
        return tag, language

    def title(self, (tag, language)):
        tag = models.Translation(tag, language)
        return u'%s » %s' % (settings.MARCUS_TITLE, tag.title())

    def link(self, (tag, language)):
        return utils.iurl(reverse('marcus-tag', args=[tag.slug]), language)

    def get_queryset(self, tag, language):
        return models.Article.public.language(language).filter(tags=tag)


class CommentFeed(object):
    title_template = 'marcus/feeds/comment_title.html'
    description_template = 'marcus/feeds/comment_summary.html'
    content_template = 'marcus/feeds/comment_content.html'
    subtitle = settings.MARCUS_SUBTITLE

    def title(self):
        return u'%s » %s' % (settings.MARCUS_TITLE, _(u'comments'))

    def items(self, (obj, language)):
        qs = self.get_queryset(obj, language).select_related(
            'author', 'author__scipio_profile', 'article', 'article__author'
        )[:settings.MARCUS_ITEMS_IN_FEED]
        return [models.Translation(c, language) for c in qs]

    def item_pubdate(self, comment):
        return comment.created

    def item_author_name(self, comment):
        return comment.author_str()

    def item_author_link(self, comment):
        if comment.type == 'comment':
            return comment.author_url()
        if comment.type == 'pingback':
            return comment.guest_url

    def updated(self, comment):
        return comment.approved


class Comment(CommentFeed, ContentFeed):
    def get_object(self, request, language):
        translation.activate(language or 'ru')
        return None, language

    def link(self, (obj, language)):
        return utils.iurl(reverse('marcus-index'), language)

    def get_queryset(self, obj, language):
        return models.Comment.public.language(language).order_by('-created')


class ArticleComment(CommentFeed, ContentFeed):
    def get_object(self, request, year, month, day, slug, language):
        translation.activate(language or 'ru')
        return get_object_or_404(
            models.Article,
            published__year=year,
            published__month=month,
            published__day=day,
            slug=slug,
        ), language

    def title(self, (article, language)):
        article = models.Translation(article, language)
        return u'%s » %s' % (article.title(), _(u'comments'))

    def link(self, (article, language)):
        article = models.Translation(article, language)
        return article.get_absolute_url()

    def get_queryset(self, article, language):
        return models.Comment.public.language(language).filter(article=article).order_by('-created')


class ArticleCommentShort(ArticleComment):
    def get_object(self, request, year, slug, language):
        translation.activate(language or 'ru')
        return get_object_or_404(
            models.Article,
            published__year=year,
            slug=slug,
        ), language

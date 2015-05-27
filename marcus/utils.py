# coding: utf-8
import re

from django.http import Http404
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.template import loader, Context
from django.shortcuts import get_object_or_404 as goo404
from django.core.mail import EmailMultiAlternatives
from django.utils import translation
from django.utils import timezone


def absolute_url(url):
    if url is None or url.startswith('http://') or url.startswith('https://'):
        return url
    return 'http://%s%s' % (Site.objects.get_current().domain, url)


def iurl(url, language):
    return url if not language else '%s%s/' % (url, language)


def altlanguage(language):
    return {'en': None, 'ru': 'en', None: 'en'}.get(language, language)


def get_language_code_in_text(text):
    """Depending of the used language in the text determines the language,
    currently does not include text quotation.

    @return "en" or "ru"
    """
    language = None
    if text:
        language = "ru" if re.search(u'[а-яА-Я]+', text) else "en"
    return language


def email_text_quote(text, width=10, prefix="|"):
    chunks = []
    text = re.sub(r'\r', r'', text, re.UNICODE)
    sections = re.findall(r'[^\n]+', text, re.UNICODE)
    for section in sections:
        words = re.findall(r'[^\s]+', section, re.UNICODE)
        while words:
            chunk = words[0:width]
            del words[0:width]
            chunks.append(u"{0} {1}".format(prefix, u" ".join(chunk)))
        chunks.append(prefix)
    return u"\n".join(chunks)


def notify_comment_context(target_comment):
    """Build context for comment
    """
    article = target_comment.article
    site = Site.objects.get_current()
    language = 'en' if article.title_en else 'ru'
    translation.activate(language)
    context = {
        'article_title': article.title(language),
        'article_link': article.full_link(language),
        'article_url': article.get_absolute_url(language),
        'site_name': site.name,
        'site_domain': site.domain,
        'sign': settings.MARCUS_TITLE,
        'comment_guest_name': target_comment.guest_name or target_comment.author.username,
        'comment_text': email_text_quote(target_comment.text, width=10, prefix="|"),
        'comment_text_html': target_comment.text,
        'comment_created': target_comment.created,
        'language': language,
    }
    return context


def notify_comment_managers(target_comment):
    """Notify MANAGERS of the blog
    """
    recipients = dict(settings.MANAGERS).values()
    assert recipients, 'Please setup settings.MANAGERS for notify about new comments'

    email = target_comment.guest_email or target_comment.author.email
    if email in recipients:
        recipients.remove(email)
    if not recipients:
        return None

    common_context = notify_comment_context(target_comment)
    common_context['comment_admin_url'] = target_comment.get_admin_url()
    context = Context(common_context)
    text_message = loader.get_template("marcus/emails/managers_comment.txt").render(context)
    html_message = loader.get_template("marcus/emails/managers_comment.html").render(context)
    subject = loader.get_template("marcus/emails/managers_comment_subject.txt").render(context).strip()
    return send_email(subject, text_message, html_message, recipients)


def notify_comment_followers(target_comment):
    """Notify followers of the article comments
    """
    common_context = notify_comment_context(target_comment)
    from marcus.models import Comment

    try:
        comments = Comment.public\
            .filter(article=target_comment.article, followup=True)\
            .exclude(guest_email='')\
            .exclude(guest_email=target_comment.guest_email)\
            .distinct('guest_email')\
            .order_by('guest_email')
        comments = list(comments)
    except NotImplementedError:
        # Temporary fix for MySQL
        comments = Comment.public\
            .filter(article=target_comment.article, followup=True)\
            .exclude(guest_email='')\
            .exclude(guest_email=target_comment.guest_email)
        comments.query.group_by = ['guest_email']

    for comment in comments:
        if not comment.guest_email:
            continue
        # Build context
        unsubscribe_url = reverse(
            "marcus-article-comments-unsubscribe",
            args=[target_comment.article_id, comment.make_token(), common_context['language']]
        )
        context = {
            'unsubscribe_url': unsubscribe_url,
        }
        context.update(common_context)
        context = Context(context)
        # Build message
        text_message = loader.get_template("marcus/emails/followup_comment.txt").render(context)
        html_message = loader.get_template("marcus/emails/followup_comment.html").render(context)
        subject = loader.get_template("marcus/emails/followup_comment_subject.txt").render(context).strip()
        # Send message
        send_email(subject, text_message, html_message, [comment.guest_email])
    return True


def send_email(subject, text_message, html_message, emails):
    message = EmailMultiAlternatives(
        subject, text_message, settings.DEFAULT_FROM_EMAIL, emails)
    message.attach_alternative(html_message, "text/html")
    return message.send()


def get_object_or_404(*args, **kwargs):
    try:
        return goo404(*args, **kwargs)
    except Http404:
        # Hack for old version of Django for saved datetimes in DB.
        # Migration is not safity, so I can't create it.
        timezone.activate(timezone.utc)
        obj = goo404(*args, **kwargs)
        timezone.deactivate()
        return obj

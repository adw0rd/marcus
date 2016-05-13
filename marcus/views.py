# coding: utf-8
import json
import scipio
import pingdjack
import datetime
from scipio.forms import AuthForm

from django import http
from django.db.models import Q
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.utils import translation
from django.contrib import auth
from django.contrib.auth.models import User
from django.conf import settings

from marcus import models, forms, antispam, utils
from marcus.utils import get_object_or_404


def object_list(request, queryset, template_name, context):
    paginator = Paginator(queryset, settings.MARCUS_PAGINATE_BY)
    try:
        page = paginator.page(int(request.GET.get('page', '1')))
    except (InvalidPage, ValueError):
        raise http.Http404()
    context.update({
        'object_list': page.object_list,
        'paginator': paginator,
        'page_obj': page,
    })
    return render(request, template_name, context)


def superuser_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated() or not request.user.is_superuser:
            return http.HttpResponseForbidden('Superuser required', content_type='text/plain')
        return func(request, *args, **kwargs)
    return wrapper


def get_ip(request):
    ip = request.META.get('REMOTE_ADDR') or models.Comment._meta.get_field('ip').default
    if ip and ip.startswith('::ffff:'):
        ip = ip[7:]
    return ip


def index(request, language):
    translation.activate(language or 'ru')
    articles = models.Article.public.language(language)[:settings.MARCUS_ARTICLES_ON_INDEX]
    comments = list(models.Comment.public.language(language).order_by('-created')[:settings.MARCUS_COMMENTS_ON_INDEX])
    for comment in comments[:settings.MARCUS_COMMENT_EXCERPTS_ON_INDEX]:
        comment.show_excerpt = True

    return render(request, 'marcus/index.html', {
        'language': language,
        'essentials': models.Category.objects.filter(essential=True),
        'categories': models.Category.objects.popular(language),
        'tags': models.Tag.objects.popular(language),
        'articles': articles,
        'comments': comments,
        'meta_description': settings.MARCUS_DESCRIPTION,
        'meta_keywords': settings.MARCUS_KEYWORDS,
    })


def category_index(request, language):
    translation.activate(language or 'ru')
    return object_list(
        request,
        models.Category.objects.language(language),
        'marcus/category_list.html',
        {'language': language},
    )


def category(request, slug, language):
    translation.activate(language or 'ru')
    category = get_object_or_404(models.Category, slug=slug)
    return object_list(
        request,
        models.Article.public.language(language).filter(categories=category),
        'marcus/category.html',
        {
            'category': models.Translation(category, language),
            'language': language,
        },
    )


def tag_index(request, language):
    translation.activate(language or 'ru')
    return render(
        request,
        'marcus/tag_list.html',
        {'language': language, 'object_list': models.Tag.objects.language(language)},
    )


def tag(request, slug, language):
    translation.activate(language or 'ru')
    tag = get_object_or_404(models.Tag, slug=slug)
    return object_list(
        request,
        models.Article.public.language(language).filter(tags=tag),
        'marcus/tag.html',
        {
            'tag': models.Translation(tag, language),
            'language': language,
        },
    )


def archive_index(request, language):
    translation.activate(language or 'ru')
    settings.USE_TZ = False
    return render(request, 'marcus/archive-index.html', {
        'language': language,
        'months': sorted(models.Article.public.language(language).dates('published', 'month'), reverse=True),
    })


def archive(request, year, month, language):
    translation.activate(language or 'ru')
    queryset = models.Article.public.language(language)
    if month:
        try:
            first = datetime.datetime.strptime('%s-%s' % (year, month), '%Y-%m')
        except ValueError:
            raise http.Http404()
        queryset = queryset.filter(published__year=year, published__month=month)
    else:
        queryset = queryset.filter(published__year=year)
    return object_list(
        request,
        queryset,
        'marcus/archive.html',
        {
            'language': language,
            'year': year,
            'month': month and first,
        },
    )


def archive_short(request, year, language):
    args = [arg for arg in (year, language, ) if arg]
    url = reverse('marcus-archive', args=args)
    return redirect(url)


def find_article(request, slug):
    translation.activate('ru')
    objs = models.Article.public.filter(slug__startswith=slug)
    if not objs:
        raise http.Http404()
    if len(objs) == 1:
        return redirect(objs[0])
    else:
        return object_list(
            request,
            objs,
            'marcus/article_choice_list.html',
            {'slug': slug, 'language': None},
        )


def _process_new_comment(request, comment, language, check_login):
    spam_status = antispam.conveyor.validate(request, comment=comment)
    if spam_status == 'spam':
        comment.delete()
        return render(request, 'marcus/spam.html', {
            'text': comment.text,
            'admins': [e for n, e in settings.ADMINS],
        })
    if check_login and not request.user.is_authenticated():
        form = AuthForm(request.session, {'openid_identifier': request.POST['name']})
        if form.is_valid():
            comment = models.Translation(comment, language)
            url = form.auth_redirect(request, target=comment.get_absolute_url(), data={'acquire': str(comment.pk)})
            return redirect(url)
    comment.spam_status = spam_status
    if spam_status == 'clean':
        comment.approved = timezone.now()
    else:
        request.session['unapproved'] = comment.pk
    comment.save()
    return redirect(models.Translation(comment, language))


def article_short(request, year, slug, language):
    obj = get_object_or_404(models.Article, published__year=year, slug=slug)
    args = [i for i in year, obj.published.month, obj.published.day, slug, language if i]
    url = reverse('marcus-article', args=args)
    return redirect(url)


def article(request, year, month, day, slug, language):
    obj = get_object_or_404(
        models.Article, published__year=year, published__month=month, published__day=day, slug=slug
    )
    guest_name = request.session.get('guest_name', '')
    guest_email = request.session.get('guest_email', '')
    translation.activate(language or obj.only_language() or 'ru')
    if request.method == 'POST':
        form = forms.CommentForm(request.user, get_ip(request), obj, language, request.POST)
        if form.is_valid():
            request.session['guest_name'] = form.cleaned_data.get('name', '')
            request.session['guest_email'] = form.cleaned_data.get('xemail', '')
            form.cleaned_data['text'] = form.cleaned_data['text'].replace('script', u'sсript')
            comment = form.save()
            return _process_new_comment(request, comment, language, True)
    else:
        form = forms.CommentForm(article=obj, language=language)

    comments = models.Comment.common.language(language)\
        .select_related('author', 'author__scipio_profile', 'article')\
        .filter(article=obj, type="comment")\
        .filter(Q(guest_name=guest_name) | ~Q(approved=None))\
        .order_by('created', 'approved')

    unapproved = False
    try:
        unapproved_pk = request.session.get('unapproved')
        if unapproved_pk:
            unapproved = models.Comment.objects.get(pk=unapproved_pk, approved=None)
    except models.Comment.DoesNotExist:
        if 'unapproved' in request.session:
            del request.session['unapproved']

    retweet_url = u'http://twitter.com/home/?status={title}%20{url}%20{suffix}'.format(
        title=obj.title(),
        url=utils.absolute_url(utils.iurl(reverse('marcus-article-short', args=[obj.published.year, obj.slug, ]), language)),
        suffix=settings.MARCUS_RETWEET_SUFFIX.replace('@', '%40')
    )

    keywords = [tag.title(language) for tag in obj.tags.all()] +\
        [category.title(language) for category in obj.categories.all()]

    return render(request, 'marcus/article.html', {
        'article': models.Translation(obj, language),
        'comments': comments,
        # 'noteworthy_count': comments.filter(noteworthy=True).count(),
        'form': not obj.comments_hidden and form,
        'unapproved': unapproved,
        'language': language,
        'guest_name': guest_name,
        'guest_email': guest_email,
        'retweet_url': retweet_url,
        'meta_keywords': ", ".join(keywords),
        'meta_description': (obj.intro(language) or "").replace('"', "'"),
    })


@superuser_required
def draft(request, pk, language):
    translation.activate(language or 'ru')
    obj = get_object_or_404(models.Article, pk=pk)
    return render(request, 'marcus/article.html', {
        'article': models.Translation(obj, language),
        'categories': (models.Translation(c, language) for c in obj.categories.all()),
        'language': language,
    })


def acquire_comment(sender, user, acquire=None, language=None, **kwargs):
    if acquire is None:
        return
    try:
        auth.login(sender, user)
        comment = models.Comment.objects.get(pk=acquire)
        comment.author = user
        comment.save()
        _process_new_comment(sender, comment, language, False)
    except models.Comment.DoesNotExist:
        pass
scipio.signals.authenticated.connect(acquire_comment)


@superuser_required
@require_POST
def approve_comment(request, id):
    comment = get_object_or_404(models.Comment, pk=id)
    antispam.conveyor.submit_ham(comment.spam_status, comment=comment)
    comment.approved = timezone.now()
    comment.save()
    if not comment.by_guest():
        scipio_profile = comment.author.scipio_profile
        if scipio_profile.spamer is None:
            scipio_profile.spamer = False
            scipio_profile.save()
    return redirect(spam_queue)


@superuser_required
@require_POST
def spam_comment(request, id):
    comment = get_object_or_404(models.Comment, pk=id)
    if not comment.by_guest():
        scipio_profile = comment.author.scipio_profile
        if scipio_profile.spamer is None:
            scipio_profile.spamer = True
            scipio_profile.save()
    antispam.conveyor.submit_spam(comment=comment)
    comment.delete()
    return redirect(comment.article)


@superuser_required
@require_POST
def delete_spam(request):
    models.Comment.suspected.all().delete()
    return redirect(spam_queue)


@superuser_required
def spam_queue(request):
    return object_list(
        request,
        models.Comment.suspected.select_related(),
        'marcus/spam_queue.html',
        {}
    )


@require_POST
def comment_preview(request):
    html = models.Comment(text=request.POST.get('text', '')).html()
    return http.HttpResponse(
        json.dumps({'status': 'valid', 'html': html}),
        content_type='application/json',
    )


def handle_pingback(sender, source_url, view, args, author, excerpt, **kwargs):
    if view != article:
        raise pingdjack.UnpingableTarget
    a = models.Article.objects.get(slug=args[3])
    if a.comments.filter(type='pingback', guest_url=source_url):
        raise pingdjack.DuplicatePing
    a.comments.create(
        type='pingback',
        text=excerpt,
        author=User.objects.get(username='marcus_guest'),
        guest_name=author,
        guest_url=source_url,
        ip=get_ip(sender),
        language=a.comment_language(args[4]),
        approved=timezone.now(),
    )
pingdjack.received.connect(handle_pingback)


def article_upload_image_preview(request, object_id):
    max_width = 300
    image_path = get_object_or_404(models.ArticleUpload, pk=object_id).upload.path

    import StringIO
    try:
        from PIL import Image
    except ImportError:
        import Image
    try:
        image = Image.open(image_path.encode('utf-8'))
    except:
        return http.HttpResponse("Not a image", content_type="text/html")

    buffer = StringIO.StringIO()
    max_width = max_width if max_width < image.size[0] else image.size[0]
    height = int((float(image.size[1]) * float(max_width / float(image.size[0]))))
    image.resize((max_width, height), Image.ANTIALIAS).save(buffer, "PNG")
    return http.HttpResponse(buffer.getvalue(), content_type="image/png")


def search(request, language):
    SEARCH_LANGUAGES = (
        (None, translation.ugettext_lazy(u'All')),
        ('en', translation.ugettext_lazy(u'English')),
    )
    search_query = request.GET.get('s', '')
    search_language = request.GET.get('l', None)
    if search_language not in dict(SEARCH_LANGUAGES).keys():
        search_language = None

    language = search_language
    translation.activate(language or 'ru')

    return object_list(
        request,
        models.Article.public.language(language).search(search_query),
        'marcus/search.html',
        {
            'search_query': search_query,
            'search_language': search_language,
            'language': language,
            'search_languages': SEARCH_LANGUAGES,
        },
    )


def article_comments_unsubscribe(request, article_id, token, language):
    language = language or translation.get_language()
    translation.activate(language)

    article = get_object_or_404(models.Article, pk=article_id)
    comments = article.comments.filter(followup=True)
    for comment in comments:
        if comment.make_token() == token:
            found_comment = comment
            comments\
                .filter(guest_email=comment.guest_email)\
                .update(followup=False)
            break
    else:
        return http.HttpResponseForbidden(
            'Token is failed or expired!', content_type='text/plain')

    return render(request, 'marcus/unsubscribe.html', {
        'article_link': mark_safe(article.link(language)),
        'guest_name': found_comment.guest_name or found_comment.guest_email,
    })

import pingdjack

from django.conf.urls import patterns, include, url

from marcus import views, feeds


urlpatterns = patterns(
    '',
    url(r'^(?:(en|ru)/)?$', views.index, name='marcus-index'),

    url(r'^category/(?:(en|ru)/)?$', views.category_index, name='marcus-categories'),
    url(r'^category/([A-Za-z0-9_-]+)/(?:(en|ru)/)?$', views.category, name='marcus-category'),
    url(r'^tag/(?:(en|ru)/)?$', views.tag_index, name='marcus-tags'),
    url(r'^tag/([A-Za-z0-9_-]+)/(?:(en|ru)/)?$', views.tag, name='marcus-tag'),
    url(r'^archive/(?:(en|ru)/)?$', views.archive_index, name='marcus-archive-index'),
    url(r'^archive/(\d{4})/(?:(\d{1,2})/)?(?:(en|ru)/)?$', views.archive, name='marcus-archive'),
    url(r'^(\d{4})/(?:(en|ru)/)?$', views.archive_short, name="marcus-archive-short"),

    url(r'^suspected/$', views.spam_queue, name='marcus-spam-queue'),
    url(r'^suspected/approve/(\d+)/$', views.approve_comment, name='marcus-approve-comment'),
    url(r'^suspected/spam/(\d+)/$', views.spam_comment, name='marcus-spam-comment'),
    url(r'^suspected/delete/$', views.delete_spam, name='marcus-delete-spam'),

    url(r'^feed/(?:(en|ru)/)?$', feeds.Article(), name='marcus-feed'),
    url(r'^category/([A-Za-z0-9_-]+)/feed/(?:(en|ru)/)?$', feeds.Category(), name='marcus-category-feed'),
    url(r'^tag/([A-Za-z0-9_-]+)/feed/(?:(en|ru)/)?$', feeds.Tag(), name='marcus-tag-feed'),
    url(r'^comments/feed/(?:(en|ru)/)?$', feeds.Comment(), name='marcus-comments-feed'),
    url(r'^(\d{4})/(\d{1,2})/(\d{1,2})/([^/]+)/feed/(?:(en|ru)/)?$', feeds.ArticleComment(), name='marcus-article-comments-feed'),
    url(r'^(\d{4})/([^/]+)/feed/(?:(en|ru)/)?$', feeds.ArticleCommentShort(), name="marcus-article-comments-feed-short"),
    url(r'^comments/unsubscribe/(\d+)/(\w+)/(?:(en|ru)/)?$', views.article_comments_unsubscribe, name="marcus-article-comments-unsubscribe"),

    url(r'^comment_preview/$', views.comment_preview, name='marcus-comment-preview'),
    url(r'^pingback/$', pingdjack.server_view, name='marcus-pingback'),

    url(r'^(\d{4})/(\d{1,2})/(\d{1,2})/([^/]+)/(?:(en|ru)/)?$', views.article, name='marcus-article'),
    url(r'^(\d{4})/([^/]+)/(?:(en|ru)/)?$', views.article_short, name='marcus-article-short'),
    url(r'^draft/(\d+)/(?:(en|ru)/)?$', views.draft, name='marcus-draft'),

    url(r'^search/(?:(en|ru)/)?$', views.search, name="marcus-search"),
    url(r'^([^/]+)/$', views.find_article, name='marcus-find-article'),

    url(r'^articleuploadimage/preview/(\d+)/$', views.article_upload_image_preview, name="article-upload-image-preview"),
    url(r'^sitemap', include('marcus.sitemap_urls')),

    url(r'^', include('scipio.urls')),
)

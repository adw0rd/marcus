from django.urls import include, path, re_path

from marcus import views, feeds


urlpatterns = [
    re_path('^(?:(en|ru)/)?$', views.index, name='index'),

    re_path('^category/(?:(en|ru)/)?$', views.category_index, name='categories'),
    re_path('^category/([A-Za-z0-9_-]+)/(?:(en|ru)/)?$', views.category, name='category'),
    re_path('^tag/(?:(en|ru)/)?$', views.tag_index, name='tags'),
    re_path('^tag/([A-Za-z0-9_-]+)/(?:(en|ru)/)?$', views.tag, name='tag'),
    re_path('^archive/(?:(en|ru)/)?$', views.archive_index, name='archive-index'),
    re_path('^archive/(\d{4})/(?:(\d{1,2})/)?(?:(en|ru)/)?$', views.archive, name='archive'),
    re_path('^(\d{4})/(?:(en|ru)/)?$', views.archive_short, name='archive-short'),

    path('suspected/', views.spam_queue, name='spam-queue'),
    path('suspected/approve/(\d+)/', views.approve_comment, name='approve-comment'),
    path('suspected/spam/(\d+)/', views.spam_comment, name='spam-comment'),
    path('suspected/delete/', views.delete_spam, name='delete-spam'),

    re_path('^feed/(?:(en|ru)/)?$', feeds.Article(), name='feed'),
    re_path('^category/([A-Za-z0-9_-]+)/feed/(?:(en|ru)/)?$', feeds.Category(), name='category-feed'),
    re_path('^tag/([A-Za-z0-9_-]+)/feed/(?:(en|ru)/)?$', feeds.Tag(), name='tag-feed'),
    re_path('^comments/feed/(?:(en|ru)/)?$', feeds.Comment(), name='comments-feed'),
    re_path('^(\d{4})/(\d{1,2})/(\d{1,2})/([^/]+)/feed/(?:(en|ru)/)?$', feeds.ArticleComment(), name='article-comments-feed'),
    re_path('^(\d{4})/([^/]+)/feed/(?:(en|ru)/)?$', feeds.ArticleCommentShort(), name='article-comments-feed-short'),
    re_path('^comments/unsubscribe/(\d+)/(\w+)/(?:(en|ru)/)?$', views.article_comments_unsubscribe, name='article-comments-unsubscribe'),
    path('comment_preview/', views.comment_preview, name='comment-preview'),

    re_path('^(\d{4})/(\d{1,2})/(\d{1,2})/([^/]+)/(?:(en|ru)/)?$', views.article, name='article'),
    re_path('^(\d{4})/([^/]+)/(?:(en|ru)/)?$', views.article_short, name='article-short'),
    re_path('^draft/(\d+)/(?:(en|ru)/)?$', views.draft, name='draft'),

    re_path('^search/(?:(en|ru)/)?$', views.search, name='search'),
    re_path('^([^/]+)/', views.find_article, name='find-article'),

    re_path('^articleuploadimage/preview/(\d+)/', views.article_upload_image_preview, name='article-upload-image-preview'),
    path('sitemap', include(('marcus.sitemap_urls', 'sitemap'))),
]

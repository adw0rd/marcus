Introduction
============

Marcus is billingual blog engine, written Ivan Sagalaev (https://softwaremaniacs.org/about/).

This fork over augmented and has the following features:

* Billingual articles, Categories, Tags and Comments
* Simple file uploader for the article with a preview images
* Archive and date navigation
* Pingback
* Automatically pings search engines on new entries
* Supports markdown (https://pypi.python.org/pypi/markdown2)
* Comments have CSRF protection via JavaScript
* There is support for retweet button
* Sitemaps for articles, feeds for articles and comments
* A simple search module
* A pretty minimalistic theme
* Import from Wordpress (command "wordpress_importer")


Examples
============

* https://softwaremaniacs.org/blog/ (Ivan Sagalaev)
* https://prudnitskiy.pro/ (Pavel Rudnitskiy)
* https://adw0rd.com/ (Mikhail Andreev)

About marcus
=============

* https://softwaremaniacs.org/blog/2010/07/19/marcus-bilingual-blog/
* https://softwaremaniacs.org/blog/2012/10/21/marcus-new-life/
* https://adw0rd.com/2012/8/8/goodbye-wordpress/

Screenshots:
=============

.. image:: https://raw.github.com/adw0rd/marcus/master/docs/screenshots/thumbnails/articles.png
    :target: https://github.com/adw0rd/marcus/blob/master/docs/screenshots/articles.png
.. image:: https://raw.github.com/adw0rd/marcus/master/docs/screenshots/thumbnails/article.png
    :target: https://github.com/adw0rd/marcus/blob/master/docs/screenshots/article.png
.. image:: https://raw.github.com/adw0rd/marcus/master/docs/screenshots/thumbnails/admin_articles.png
    :target: https://github.com/adw0rd/marcus/blob/master/docs/screenshots/admin_articles.png
.. image:: https://raw.github.com/adw0rd/marcus/master/docs/screenshots/thumbnails/admin_article.png
    :target: https://github.com/adw0rd/marcus/blob/master/docs/screenshots/admin_article.png


Installation
=============

https://pypi.python.org/pypi/django-marcus
::

    mkvirtualenv marcus
    pip install --process-dependency-links django-marcus  # use "--process-dependency-links" for pip>=1.5
    django-admin.py startproject <project_name>


Configuration
==============

Add to ``settings.py``::

    import os
    import imp
    
    PROJECT_ROOT = os.path.dirname(__file__)
    PROJECT_NAME = os.path.basename(PROJECT_ROOT)
    STORAGE_ROOT = os.path.join('/storage', PROJECT_NAME)
    LOCALE_PATHS = (
        os.path.join(imp.find_module('marcus')[1], 'locale'),
    )

    ADMINS = (
        ('Admin', 'admin@example.com'),
    )
    // Please setup settings.MANAGERS for notify about new comments
    MANAGERS = ADMINS

    MARCUS_PAGINATE_BY = 20
    MARCUS_ARTICLES_ON_INDEX = 10
    MARCUS_COMMENTS_ON_INDEX = 10
    MARCUS_COMMENT_EXCERPTS_ON_INDEX = 2
    MARCUS_ITEMS_IN_FEED = 20
    MARCUS_AUTHOR_ID = 1
    MARCUS_TAG_MINIMUM_ARTICLES = 0
    
    # Specify blog names:
    from django.utils.translation import ugettext_lazy as _
    MARCUS_TITLE = _('Blog')
    MARCUS_SUBTITLE = _('Sample blog')
    
    MARCUS_DESCRIPTION = _('')
    MARCUS_KEYWORDS = _('')

    # You can specify extras for markdown:
    MARCUS_MARKDOWN_EXTRAS = ['code-friendly', 'wiki-tables']
    
    # You can specify #hashtag or @name as suffix for Twitter:
    MARCUS_RETWEET_SUFFIX = "#marcus"

    # Specify a fields which will used in search:
    MARCUS_SEARCH_FIELDS = [
        'slug', 'title_ru', 'title_en', 'text_ru', 'text_en',
        'categories__slug', 'categories__title_ru', 'categories__title_en',
    ]

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
    )
    
    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.request',
        'marcus.context_processors.marcus_context',
    )

    MEDIA_ROOT = os.path.join(STORAGE_ROOT, 'media')
    MEDIA_URL = '/media/'
    
    STATIC_ROOT = os.path.join(STORAGE_ROOT, 'static')
    STATIC_URL = '/static/'
    
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.admindocs',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.flatpages',
        'marcus'
    )


Add to ``urls.py``::

    from django.conf.urls import patterns, include, url
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.contrib import admin
    
    admin.autodiscover()
    
    urlpatterns = patterns('',
        url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
        url(r'^admin/', include(admin.site.urls)),
        url(r'^', include('marcus.urls')),
    )
    
    urlpatterns += staticfiles_urlpatterns()



And run so::

    python ./manage.py runserver 8000



Wordpress importer settings:
-----------------------------

Marcus includes "wordpress_importer" it is command that imports your entries from the Wordpress to the Marcus.
It has a built-in pipelines for additional filtering data.
::

    MARCUS_WORDPRESS_IMPORTER = {
        'ARTICLE_PIPELINES': (
            'marcus.wordpress_importer.pipelines.CodecolorerToHighlightJsPipeline',
            'marcus.wordpress_importer.pipelines.WpContentUploadsToMediaPipeline',
            'marcus.wordpress_importer.pipelines.BbCodeDetector',
            'marcus.wordpress_importer.pipelines.EscapeTheUnderscore',
            # 'marcus.wordpress_importer.pipelines.ChangeUrlToArticleForImagePipeline',
            # 'marcus.wordpress_importer.pipelines.RemoveImgClassPipeline',
            # 'marcus.wordpress_importer.pipelines.HtmlToMarkdownPipeline',
        ),
        # 'CATEGORY_PIPELINES': tuple(),
        # 'TAG_PIPELINES': tuple(),
        'COMMENT_PIPELINES': (
            'marcus.wordpress_importer.pipelines.CodecolorerToHighlightJsPipeline',
        ),
        'ALLOW_DOMAINS': (  # Used to determine the internal domain to import only local "wp-content/uploads", etc.
            'my-old-blog-on-wordpress.org',
            'www.my-old-blog-on-wordpress.org',
        ),
    }


Installation guide for new projects:
======================================
::

    django-admin.py startproject project
    cd project
    pip install --process-dependency-links django-marcus  # use "--process-dependency-links" for pip>=1.5
    ... Copy the settings to settings.py and you urls to you urls.py described above ...
    python ./manage.py syncdb
    python ./manage.py createsuperuser
    python ./manage.py runserver 8000


MySQL Timezone Fixes
=====================

If you use MySQL and have problem with open an article by URL, it is likely that you did not work ``CONVERT_TZ``, it can be solved as follows::

    mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p mysql


License
========

BSD licensed.

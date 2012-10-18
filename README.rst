Introduction
============

Marcus is billingual blog engine, written Ivan Sagalaev (http://softwaremaniacs.org/about/).

This fork over augmented and has the following features:

* Articles, Categories, Tags entities
* File uploader for Articles with output thumbnails then file is picture
* Sitemaps for articles, Feeds for articles and comments
* Simple search module
* Beautiful theme (Coming soon)
* Wordpress Import (command named "wordpress_importer")


Examples
============

* http://softwaremaniacs.org/blog/ (The author blog)
* http://adw0rd.com/ (The maintainer blog)


Screenshots:
============

    Сoming soon


Installation
============

From PyPI:
------------
::

    pip install marcus

From sources:
--------------
::

    git clone git://github.com/adw0rd/marcus.git marcus
    cd marcus
    virtualenv --no-site-packages venv
    source venv/bin/activate
    pip install -r requirements.txt
    python ./manage.py runserver 8000


Common settings:
-----------------
::

    MARCUS_PAGINATE_BY = 20
    MARCUS_ARTICLES_ON_INDEX = 10
    MARCUS_COMMENTS_ON_INDEX = 10
    MARCUS_COMMENT_EXCERPTS_ON_INDEX = 2
    MARCUS_ITEMS_IN_FEED = 20
    MARCUS_AUTHOR_ID = 1
    
    # Specify blog names:
    from django.utils.translation import ugettext_lazy as _
    MARCUS_TITLE = _('Blog')
    MARCUS_SUBTITLE = _('Sample blog')
    
    MARCUS_MARKDOWN_EXTRAS = ['code-friendly', 'wiki-tables']

    # Specify a fields which will used in search:
    MARCUS_SEARCH_FIELDS = [
        'slug', 'title_ru', 'title_en', 'text_ru', 'text_en',
        'categories__slug', 'categories__title_ru', 'categories__title_en',
    ]
    
    # OpenID sessions dir. OpenID authentication will not work without it.
    SCIPIO_STORE_ROOT = '/path/to/scipio'
    
    # URL passed to OpenID-provider to identify site that requests authentication.
    # Should not end with '/'.
    # Complete site URL is passed if the value is empty.
    SCIPIO_TRUST_URL = ''
    SCIPIO_AKISMET_KEY = ''  # You can receive the key here https://akismet.com/signup/
    
    SCIPIO_USE_CONTRIB_SITES = True
    
    AUTHENTICATION_BACKENDS = (
        'scipio.authentication.OpenIdBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

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


Example of the ``urls.py``:
-----------------------------
::

    from django.conf.urls import patterns, include, url
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.contrib import admin
    
    admin.autodiscover()
    
    urlpatterns = patterns('',
        url(r'^', include('marcus.urls')),
        url(r'^', include('subhub.urls')),
        url(r'^', include('scipio.urls')),
        url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
        url(r'^admin/', include(admin.site.urls)),
        url(r'^sitemap', include('marcus.sitemap_urls')),
    )
    
    urlpatterns += staticfiles_urlpatterns()

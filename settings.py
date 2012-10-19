import os
import marcus

PROJECT_ROOT = os.path.dirname(__file__)
PROJECT_NAME = os.path.basename(PROJECT_ROOT)
STORAGE_ROOT = os.path.join('/storage', PROJECT_NAME)
MARCUS_ROOT = os.path.dirname(marcus.__file__)
LOCALE_PATHS = (
    os.path.join(MARCUS_ROOT, 'locale'),
)

MARCUS_PAGINATE_BY = 20
MARCUS_ARTICLES_ON_INDEX = 10
MARCUS_COMMENTS_ON_INDEX = 10
MARCUS_COMMENT_EXCERPTS_ON_INDEX = 2
MARCUS_ITEMS_IN_FEED = 20
MARCUS_AUTHOR_ID = 1
MARCUS_TAG_MINIMUM_ARTICLES = 3

# Specify blog names:
from django.utils.translation import ugettext_lazy as _
MARCUS_TITLE = _('Blog')
MARCUS_SUBTITLE = _('Sample blog')

# You can specify extras for markdown:
MARCUS_MARKDOWN_EXTRAS = ['code-friendly', 'wiki-tables']

# You can specify #hashtag or @name as suffix for Twitter:
MARCUS_RETWEET_SUFFIX = "#marcus"

# Specify a fields which will used in search:
MARCUS_SEARCH_FIELDS = [
    'slug', 'title_ru', 'title_en', 'text_ru', 'text_en',
    'categories__slug', 'categories__title_ru', 'categories__title_en',
]

# OpenID sessions dir. OpenID authentication will not work without it.
SCIPIO_STORE_ROOT = os.path.join(STORAGE_ROOT, 'scipio')

# URL passed to OpenID-provider to identify site that requests authentication.
# Should not end with '/'.
# Complete site URL is passed if the value is empty.
SCIPIO_TRUST_URL = ''

# Akismet is a spam filtering service.
# Without the key will not work comments.
# You can receive the key here https://akismet.com/signup/
SCIPIO_AKISMET_KEY = ''

SCIPIO_USE_CONTRIB_SITES = True

AUTHENTICATION_BACKENDS = (
    'scipio.authentication.OpenIdBackend',
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
    'marcus',
    'subhub',
    'scipio',
)

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
    'ALLOW_DOMAINS': (
        'my-old-blog-on-wordpress.org',
        'www.my-old-blog-on-wordpress.org',
    ),
}

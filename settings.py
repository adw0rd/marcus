import os
import imp
from django.utils.translation import ugettext_lazy as _

PROJECT_ROOT = os.path.dirname(__file__)
PROJECT_NAME = os.path.basename(PROJECT_ROOT)
STORAGE_ROOT = os.path.join('/storage', PROJECT_NAME)
LOCALE_PATHS = (
    os.path.join(imp.find_module('marcus')[1], 'locale'),
)

MARCUS_PAGINATE_BY = 20
MARCUS_ARTICLES_ON_INDEX = 10
MARCUS_COMMENTS_ON_INDEX = 10
MARCUS_COMMENT_EXCERPTS_ON_INDEX = 2
MARCUS_ITEMS_IN_FEED = 20
MARCUS_AUTHOR_ID = 1
MARCUS_TAG_MINIMUM_ARTICLES = 0

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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'marcus.context_processors.marcus_context',
            ],
        },
    },
]

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
    'martor',
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

# coding: utf-8

MARCUS_PAGINATE_BY = 20
MARCUS_ARTICLES_ON_INDEX = 10
MARCUS_COMMENTS_ON_INDEX = 10
MARCUS_COMMENT_EXCERPTS_ON_INDEX = 2
MARCUS_ITEMS_IN_FEED = 20
MARCUS_AUTHOR_ID = 1
MARCUS_TITLE = 'Blog'
MARCUS_SUBTITLE = 'Sample blog'

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

# OpenID sessions dir.
# OpenID authentication will not work without it.
SCIPIO_STORE_ROOT = '/path/to/scipio'

# URL passed to OpenID-provider to identify site that requests authentication.
# Should not end with '/'.
# Complete site URL is passed if the value is empty.
SCIPIO_TRUST_URL = ''
SCIPIO_AKISMET_KEY = ''

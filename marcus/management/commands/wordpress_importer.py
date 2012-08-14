# coding: utf-8
import re
import os
import sys
from urllib2 import urlopen
from datetime import datetime
from optparse import make_option
from xml.etree import ElementTree as ET

from django.conf import settings
from django.utils import timezone
from django.core.files import File
from django.utils.text import Truncator
from django.utils.html import strip_tags
from django.db.utils import IntegrityError
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management.base import CommandError
from django.core.management.base import LabelCommand
from django.core.files.temp import NamedTemporaryFile
from django.utils.importlib import import_module

from marcus.models import Article, Tag, Category, Comment
# from marcus.utils import get_language_code_in_text

MARCUS_GUEST = User.objects.get(username="marcus_guest")
PINGBACK = 'pingback'
TRACKBACK = 'trackback'

if settings.DEBUG is True:
    # Cleanup models
    Article.objects.all().delete()
    Category.objects.all().delete()
    Tag.objects.all().delete()
    Comment.objects.all().delete()

WP_NS = 'http://wordpress.org/export/%s/'
ARTICLE_PIPELINES = settings.MARCUS_WORDPRESS_IMPORTER.get('ARTICLE_PIPELINES', tuple())
CATEGORY_PIPELINES = settings.MARCUS_WORDPRESS_IMPORTER.get('CATEGORY_PIPELINES', tuple())
TAG_PIPELINES = settings.MARCUS_WORDPRESS_IMPORTER.get('TAG_PIPELINES', tuple())
COMMENT_PIPELINES = settings.MARCUS_WORDPRESS_IMPORTER.get('COMMENT_PIPELINES', tuple())


class Command(LabelCommand):
    """Command for importing a WordPress blog into Marcus via a WordPress Export file."""
    help = 'Import a Wordpress blog into Marcus.'
    label = 'WXR file'
    args = 'wordpress.xml'

    option_list = LabelCommand.option_list + (
        make_option(
            '--noautoexcerpt',
            action='store_false',
            dest='auto_excerpt',
            default=True,
            help='Do NOT generate an excerpt if not present.'),
        make_option(
            '--author',
            dest='author',
            default='',
            help='All imported articles belong to specified author'))

    SITE = Site.objects.get_current()

    def __init__(self):
        """Init the Command and add custom styles"""
        super(Command, self).__init__()
        self.style.TITLE = self.style.SQL_FIELD
        self.style.STEP = self.style.SQL_COLTYPE
        self.style.ITEM = self.style.HTTP_INFO

    def write_out(self, message, verbosity_level=1):
        """Convenient method for outputing"""
        if self.verbosity and self.verbosity >= verbosity_level:
            sys.stdout.write(smart_str(message))
            sys.stdout.flush()

    def handle_label(self, wxr_file, **options):
        global WP_NS
        self.verbosity = int(options.get('verbosity', 1))
        self.auto_excerpt = options.get('auto_excerpt', True)
        self.default_author = options.get('author')
        if self.default_author:
            try:
                self.default_author = User.objects.get(username=self.default_author)
            except User.DoesNotExist:
                raise CommandError('Invalid username for default author')

        self.write_out(self.style.TITLE('Starting migration from Wordpress to Marcus!\n'))

        tree = ET.parse(wxr_file)
        WP_NS = WP_NS % self.guess_wxr_version(tree)

        self.authors = self.import_authors(tree)
        self.categories = self.import_categories(tree.findall('channel/{%s}category' % WP_NS))
        self.tags = self.import_tags(tree.findall('channel/{%s}tag' % WP_NS))
        self.articles = self.import_articles(tree.findall('channel/item'))

    def guess_wxr_version(self, tree):
        """We will try to guess the wxr version used
        to complete the wordpress xml namespace name"""
        for v in ('1.2', '1.1', '1.0'):
            try:
                tree.find('channel/{%s}wxr_version' % (WP_NS % v)).text
                return v
            except AttributeError:
                pass
        raise CommandError('Cannot resolve the wordpress namespace')

    def import_authors(self, tree):
        """Retrieve all the authors used in posts
        and convert it to new or existing user, and
        return the convertion"""
        self.write_out(self.style.STEP('- Importing authors\n'))
        post_authors = set()
        for item in tree.findall('channel/item'):
            post_type = item.find('{%s}post_type' % WP_NS).text
            if post_type == 'post':
                post_authors.add(item.find('{http://purl.org/dc/elements/1.1/}creator').text)

        self.write_out('> %i authors found.\n' % len(post_authors))

        authors = {}
        for post_author in post_authors:
            if self.default_author:
                authors[post_author] = self.default_author
            else:
                authors[post_author] = self.migrate_author(post_author)
        return authors

    def migrate_author(self, author_name):
        """Handle actions for migrating the users"""
        action_text = "The author '%s' needs to be migrated to an User:\n"\
                      "1. Use an existing user ?\n"\
                      "2. Create a new user ?\n"\
                      "Please select a choice: " % self.style.ITEM(author_name)
        while 42:
            selection = raw_input(smart_str(action_text))
            if selection and selection in '12':
                break
        if selection == '1':
            users = User.objects.all()
            if users.count() == 1:
                preselected_user = None
                usernames = ['[%s]' % users[0].username]
            else:
                usernames = []
                preselected_user = None
                for user in users:
                    if user.username == author_name:
                        usernames.append('[%s]' % user.username)
                        preselected_user = author_name
                    else:
                        usernames.append(user.username)
            while 42:
                user_text = "1. Select your user, by typing " \
                            "one of theses usernames:\n"\
                            "%s or 'back'\n"\
                            "Please select a choice: " % ', '.join(usernames)
                user_selected = raw_input(user_text)
                if user_selected in usernames:
                    break
                if user_selected == '' and preselected_user:
                    user_selected = preselected_user
                    break
                if user_selected.strip() == 'back':
                    return self.migrate_author(author_name)
            return users.get(username=user_selected)
        else:
            create_text = "2. Please type the email of " \
                          "the '%s' user or 'back': " % author_name
            author_mail = raw_input(create_text)
            if author_mail.strip() == 'back':
                return self.migrate_author(author_name)
            try:
                return User.objects.create_user(author_name, author_mail)
            except IntegrityError:
                return User.objects.get(username=author_name)

    def import_categories(self, category_nodes):
        """Import all the categories from 'wp:category' nodes,
        because categories in 'item' nodes are not necessarily
        all the categories and returning it in a dict for
        database optimizations."""
        self.write_out(self.style.STEP('- Importing categories\n'))

        categories = {}
        for category_node in category_nodes:
            category_data = {}
            title = category_node.find('{%s}cat_name' % WP_NS).text[:255]
            slug = category_node.find('{%s}category_nicename' % WP_NS).text[:255]
            try:
                parent_title = category_node.find('{%s}category_parent' % WP_NS).text[:255]
            except TypeError:
                parent_title = None

            category_data = {'title': title, 'slug': slug, 'parent_title': parent_title}
            self.write_out(u'> {title}... '.format(title=title))

            for pipeline_path in CATEGORY_PIPELINES:
                category_data = self._get_pipeline(pipeline_path)(data=category_data).output()

            category, created = Category.objects.get_or_create(
                title_ru=category_data.get('title'),
                slug=category_data.get('slug'),
                parent=categories.get(parent_title))

            categories[title] = category

            self.write_out(self.style.ITEM('OK\n'))

        return categories

    def import_tags(self, tag_nodes):
        """Import all the tags form 'wp:tag' nodes,
        because tags in 'item' nodes are not necessarily
        all the tags, then use only the nicename, because it's like
        a slug and the true tag name may be not valid for url usage."""

        self.write_out(self.style.STEP('- Importing tags\n'))

        tags = {}
        for tag_node in tag_nodes:
            name = tag_node.find('{%s}tag_name' % WP_NS).text[:50]
            slug = tag_node.find('{%s}tag_slug' % WP_NS).text[:50]

            tag_data = {'name': name, 'slug': slug}
            self.write_out(u'> {name}... '.format(name=name))

            for pipeline_path in TAG_PIPELINES:
                tag_data = self._get_pipeline(pipeline_path)(data=tag_data).output()

            tag_name = tag_data.get('name')
            is_english_tag = bool(re.search(u'[^а-яА-Я]+', tag_name))

            tag_ = dict(title_ru=tag_data.get('name'), slug=tag_data.get('slug'))
            if is_english_tag:
                tag_.update(dict(title_en=tag_name))

            tag, created = Tag.objects.get_or_create(**tag_)

            tags[tag_name] = tag
            self.write_out(self.style.ITEM('OK\n'))

        return tags

    def get_article_tags(self, category_nodes):
        """Return a list of article's tags,
        by using the nicename for url compatibility"""
        tags = []
        for category_node in category_nodes:
            domain = category_node.attrib.get('domain')
            if domain == 'post_tag':
                tags.append(category_node.text)
        return tags

    def get_article_categories(self, category_nodes):
        """Return a list of article's categories
        based of imported categories"""
        categories = []
        for category_node in category_nodes:
            domain = category_node.attrib.get('domain')
            if domain == 'category':
                categories.append(category_node.text)
        return categories

    def import_article(self, title, content, item_node):
        """Importing an article but some data are missing like
        related articles, start_publication and end_publication.
        start_publication and creation_date will use the same value,
        wich is always in Wordpress $post->post_date"""
        creation_date = datetime.strptime(item_node.find('{%s}post_date' % WP_NS).text, '%Y-%m-%d %H:%M:%S')
        pub_date = datetime.strptime(item_node.find('pubDate').text, '%a, %d %b %Y %H:%M:%S +0000')
        if settings.USE_TZ:
            creation_date = timezone.make_aware(creation_date, timezone.utc)
            pub_date = timezone.make_aware(pub_date, timezone.utc)

        excerpt = item_node.find('{%sexcerpt/}encoded' % WP_NS).text
        if not excerpt:
            if self.auto_excerpt:
                excerpt = Truncator('...').words(50, strip_tags(content))
            else:
                excerpt = ''

        article_data = {
            'title': title,
            'content': content,
            'excerpt': excerpt,
            # Prefer use this function than
            # item_node.find('{%s}post_name' % WP_NS).text
            # Because slug can be not well formated
            # 'slug': slugify(title)[:255] or 'post-%s' % item_node.find('{%s}post_id' % WP_NS).text,
            'slug': item_node.find('{%s}post_name' % WP_NS).text,
            'categories': self.get_article_categories(item_node.findall('category')),
            'tags': self.get_article_tags(item_node.findall('category')),
            'status': item_node.find('{%s}status' % WP_NS).text,
            'comment_enabled': item_node.find('{%s}comment_status' % WP_NS).text == 'open',
            'pingback_enabled': item_node.find('{%s}ping_status' % WP_NS).text == 'open',
            'creation_date': creation_date,
            'pub_date': pub_date,
        }

        return article_data

    def import_articles(self, items):
        """Loops over items and find article to import,
        an article need to have 'post_type' set to 'post' and
        have content."""
        self.write_out(self.style.STEP('- Importing articles\n'))

        for item_node in items:
            title = (item_node.find('title').text or '')[:255]
            post_type = item_node.find('{%s}post_type' % WP_NS).text
            content = item_node.find('{http://purl.org/rss/1.0/modules/content/}encoded').text

            if post_type == 'post' and title:
                article_data = self.import_article(title, content, item_node)

                for pipeline_path in ARTICLE_PIPELINES:
                    article_data = self._get_pipeline(pipeline_path)(data=article_data).output()

                status = article_data.get('status')
                self.write_out(u'> {title}, {status}... '.format(title=title, status=status))

                article, created = Article.objects.get_or_create(
                    slug=article_data.get('slug'),
                    title_ru=article_data.get('title'),
                    text_ru=article_data.get('content'),
                    published=article_data.get('pub_date') if status == "publish" else None,
                    updated=article_data.get('creation_date'),
                    comments_hidden=not article_data.get('comment_enabled'))

                for category_name in article_data.get('categories'):
                    category = self.categories.get(category_name)
                    if category:
                        article.categories.add(category)

                for tag_name in article_data.get('tags'):
                    tag = self.tags.get(tag_name)
                    if tag:
                        article.tags.add(tag)

                # article.authors.add(self.authors[item_node.find('{http://purl.org/dc/elements/1.1/}creator').text])
                # article.sites.add(self.SITE)

                self.write_out(self.style.ITEM('OK\n'))

                image_id = self.find_image_id(item_node.findall('{%s}postmeta' % WP_NS))
                if image_id:
                    self.import_image(article, items, image_id)

                self.import_comments(article, item_node.findall('{%s}comment' % WP_NS))
            else:
                self.write_out(u'> {title}... '.format(title=title), 2)
                self.write_out(self.style.NOTICE('SKIPPED (not a post)\n'), 2)

    def find_image_id(self, metadatas):
        for meta in metadatas:
            if meta.find('{%s}meta_key' % WP_NS).text == '_thumbnail_id':
                return meta.find('{%s}meta_value/' % WP_NS).text

    def import_image(self, article, items, image_id):
        for item in items:
            post_type = item.find('{%s}post_type' % WP_NS).text
            if post_type == 'attachment' and item.find('{%s}post_id' % WP_NS).text == image_id:

                title = u'Attachment {title}'.format(title=item.find('title').text)
                self.write_out(u' > {title}... '.format(title=title))

                image_url = item.find('{%s}attachment_url' % WP_NS).text
                img_tmp = NamedTemporaryFile(delete=True)
                img_tmp.write(urlopen(image_url).read())
                img_tmp.flush()
                article.image.save(os.path.basename(image_url), File(img_tmp))

                self.write_out(self.style.ITEM('OK\n'))

    def import_comments(self, article, comment_nodes):
        """Loops over comments nodes and import then
        in django.contrib.comments"""
        for comment_node in comment_nodes:
            is_pingback = comment_node.find('{%s}comment_type' % WP_NS).text == PINGBACK
            # is_trackback = comment_node.find('{%s}comment_type' % WP_NS).text == TRACKBACK

            comment_data = {}
            comment_data['article'] = article
            comment_data['id'] = comment_node.find('{%s}comment_id' % WP_NS).text
            comment_data['type'] = "pingback" if is_pingback else "comment"
            comment_data['text'] = comment_node.find('{%s}comment_content' % WP_NS).text
            comment_data['language'] = 'ru'  # get_language_code_in_text(comment_data['text'] or '')

            comment_data['guest_name'] = comment_node.find('{%s}comment_author' % WP_NS).text or ''
            comment_data['guest_email'] = comment_node.find('{%s}comment_author_email' % WP_NS).text or ''
            comment_data['guest_url'] = comment_node.find('{%s}comment_author_url' % WP_NS).text or ''
            comment_data['ip'] = comment_node.find('{%s}comment_author_IP' % WP_NS).text

            try:
                user = User.objects.get(username=comment_data['guest_name'])
            except User.DoesNotExist:
                user = MARCUS_GUEST
            comment_data['author'] = user

            comment_data['created'] = datetime.strptime(comment_node.find('{%s}comment_date' % WP_NS).text, '%Y-%m-%d %H:%M:%S')
            if settings.USE_TZ:
                comment_data['created'] = timezone.make_aware(comment_data['created'], timezone.utc)

            comment_approved = comment_node.find('{%s}comment_approved' % WP_NS).text
            if comment_approved == "1":
                comment_data['approved'] = comment_data['created']
            elif comment_approved == "spam":
                comment_data['spam_status'] = "spam"  # What should I write here?

            title = u'Comment #{number} by {author}'.format(number=comment_data['id'], author=comment_data['guest_name'])
            self.write_out(u' > {title}... '.format(title=title))

            for pipeline_path in COMMENT_PIPELINES:
                comment_data = self._get_pipeline(pipeline_path)(data=comment_data).output()

            if not comment_data['text']:
                self.write_out(self.style.NOTICE('SKIPPED (unfilled)\n'))
                return None

            Comment.objects.create(**comment_data)

            self.write_out(self.style.ITEM('OK\n'))

    def _get_pipeline(self, pipeline_path):
        module_name, class_name = pipeline_path.rsplit('.', 1)
        module = import_module(module_name)
        return module.__dict__.get(class_name)

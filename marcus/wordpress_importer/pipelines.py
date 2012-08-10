# coding: utf-8
import re
import os
import urllib2
import html2text
import urlparse

from django.core.urlresolvers import reverse, NoReverseMatch
from django.conf import settings

from marcus.wordpress_importer import BasePipeline


class EscapeTheUnderscore(BasePipeline):

    def replace_content(self, content):
        content = content.replace('_', '\_')
        items = []
        items.extend(re.findall('\<img[^\>]+\>', content, re.S | re.U | re.M))
        items.extend(re.findall('\<code[^\>]*\>.+?\<\/code\>', content, re.S | re.U | re.M))
        items.extend(re.findall('\<h\d{1}[^\>]*\>.+?\<\/h\d{1}\>', content, re.S | re.U | re.M))
        for item in items:
            new_item = item.replace('\_', '_')
            content = content.replace(item, new_item)
        return content


class BbCodeDetector(BasePipeline):

    def bb_caption_replace(self, content):
        """ Example: http://adw0rd.loc/2008/kupil-sebe-monitorchik/ru/
        [caption id="" align="alignnone" width="375" caption=" "].+[/caption]
        """
        content = re.sub('\[caption[^\]]+?\](.+?)\[\/caption\]', r'\1', content)
        return content

    def replace_content(self, content):
        if content.find('[caption') != -1:
            content = self.bb_caption_replace(content)
        return content


class CodecolorerToHighlightJsPipeline(BasePipeline):

    def replace_text(self, text):
        return self.replace_content(text)

    def replace_content(self, content):
        # From BB-code to html
        content = re.sub(r'\[cc([^\]]*)\]', r'<code\1>', content)
        content = content.replace('[/cc]', '</code>')

        # Convert </> to &lt;/&gt; into <code></code>
        blocks = []
        blocks.extend(re.findall(r'(\<code.*?\>)(.*?)(\<\/code\>)', content, re.M | re.U | re.S))
        # blocks.extend(re.findall(r'(\<blockquote.*?\>)(.*?)(\<\/blockquote\>)', content, re.M | re.U | re.S))
        for block in blocks:
            new_block = block[1].replace('<', '&lt;').replace('>', '&gt;')
            content = content.replace(block[1], new_block)

        # To highlight.js
        content = content.replace('<code lang=', '<code class=')
        content = content.replace('<code', '<pre><code')
        content = content.replace('</code>', '</code></pre>')

        return content


class WpContentUploadsToMediaPipeline(BasePipeline):

    ALLOW_DOMAINS = settings.MARCUS_WORDPRESS_IMPORTER.get('ALLOW_DOMAINS', tuple())

    def download_and_save(self, url):
        try:
            url_path = urlparse.urlparse(url).path
        except ValueError:
            return None

        file_path = url_path.replace('wp-content/uploads/', '')
        file_path = file_path.split('/')
        file_path, file_name = file_path[:-1], file_path[-1]
        media_root_path = os.path.join(settings.MEDIA_ROOT, *file_path)
        media_url_path = os.path.join(settings.MEDIA_URL, *file_path)

        try:
            os.makedirs(media_root_path)
        except OSError:
            pass

        try:
            # if settings.DEBUG is False:
            open(os.path.join(media_root_path, file_name), 'w').write(urllib2.urlopen(url).read())
        except (urllib2.HTTPError, urllib2.URLError), e:
            print e

        print "└─ Downloaded {url}".format(url=url)

        return os.path.join(media_url_path, file_name)

    def replace_content(self, content):
        domains = self.ALLOW_DOMAINS + ('', )  # Also available without the domain
        for domain in domains:
            scheme_and_host = 'http://{domain}'.format(domain=domain) if domain else ''
            url_paths = re.findall(
                'src\=\"{scheme_and_host}(\/wp-content\/uploads\/.+?)\"'.format(scheme_and_host=scheme_and_host),
                content) or []
            for url_path in url_paths:
                if not scheme_and_host:
                    scheme_and_host = 'http://{domain}'.format(domain=domains[0])
                url = scheme_and_host + url_path
                new_url = self.download_and_save(url)
                content = content.replace(url, new_url)
        return content


class ChangeUrlToArticleForImagePipeline(BasePipeline):
    """Change address link to article from /2012/slug-name/ to /2012/12/31/slug-name/
    """
    def replace_content(self, content):
        slug = self.data.get('slug')
        pub_date = self.data.get('pub_date')
        if slug and pub_date:
            # If you have something to change
            urls = re.findall('href\=\"(.+?\/{slug}\/)\"'.format(slug=slug), content) or []
            for url in urls:
                try:
                    new_url = reverse('marcus-article', args=[pub_date.year, pub_date.month, pub_date.day, slug])
                    content = content.replace(url, new_url)
                except NoReverseMatch:
                    pass
        return content


class RemoveImgClassPipeline(BasePipeline):
    """Remove .alignleft .wp-imaga and other classes into <img/>
    """

    def replace_content(self, content):
        for img in re.findall('\<img.+?(class\=\".+?\").+?\>', content, re.S | re.M) or []:
            content = content.replace(img, '')
        return content


class HtmlToMarkdownPipeline(BasePipeline):
    """Convert Html to Markdown. I recommended use it at the end pipelines
    """
    def replace_content(self, content):
        return html2text.html2text(content)


class ReplaceCommentedMoreToAnchored(BasePipeline):

    def replace_content(self, content):
        content = re.sub(r'<!--\s*more\s*-->', r'<a name="more"></a>', content)
        return content

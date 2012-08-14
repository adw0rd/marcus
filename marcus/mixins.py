# coding: utf-8
from marcus import models


class ArticleTextSizeAdminMixin(object):
    max_text_size = models.Article.objects\
        .extra(select={'text_length': 'if(char_length(text_ru)>char_length(text_en),char_length(text_ru),char_length(text_en))'})\
        .order_by('-text_length')[0].text_length

    def text_size(self, article):
        percent = int((len(article.html()) * 100) / self.max_text_size)
        return '<div style="width:{percent}%;height:15px;background-color:#5B80B2"></div>'.format(percent=int(percent) or 1)
    text_size.allow_tags = True

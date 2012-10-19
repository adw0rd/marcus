from django.db.utils import DatabaseError

from marcus import models


class ArticleTextSizeAdminMixin(object):
    max_text_sizes = models.Article.objects\
        .extra(select={'text_length': 'if(char_length(text_ru)>char_length(text_en),char_length(text_ru),char_length(text_en))'})\
        .order_by('-text_length')\
        .values('text_length')[0:5]

    def text_size(self, article):
        try:
            max_text_sizes = [i['text_length'] for i in self.max_text_sizes]
            max_text_size = int(sum(max_text_sizes) / len(max_text_sizes))
            percent = int((len(article.html()) * 100) / max_text_size)
        except (DatabaseError, ZeroDivisionError, ):
            # Because that in SQLite "if" there is no function.
            percent = 0
        return '<div style="width:100px;overflow:hidden"><div style="width:{percent}%;height:15px;background-color:#5B80B2">'\
               '</div></div>'.format(percent=int(percent) or 1)
    text_size.allow_tags = True

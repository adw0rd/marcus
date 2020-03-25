from django import forms
from django.contrib import admin

from marcus import models, actions, widgets


class TimedBooleanFilter(admin.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__isnull' % field.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        super(TimedBooleanFilter, self).__init__(field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def choices(self, cl):
        for k, v in [('All', None), ('Yes', ''), ('No', '1')]:
            yield {
                'selected': self.lookup_val == v,
                'query_string': cl.get_query_string({self.lookup_kwarg: v}, []),
                'display': k,
            }


class ArticleUploadForm(forms.ModelForm):
    upload = forms.FileField(widget=widgets.AdminImageWidget)


class ArticleUploadInlineAdmin(admin.TabularInline):
    model = models.ArticleUpload
    form = ArticleUploadForm


class ArticleForm(forms.ModelForm):
    class Meta:
        model = models.Article
        fields = '__all__'
        widgets = {
            'title_ru': forms.TextInput(attrs={'size': 80}),
            'text_ru': forms.Textarea(attrs={'cols': 80, 'rows': 30}),
            'title_en': forms.TextInput(attrs={'size': 80}),
            'text_en': forms.Textarea(attrs={'cols': 80, 'rows': 30}),
        }

    def clean(self):
        cleaned_data = super(ArticleForm, self).clean()
        title_ru = cleaned_data['title_ru']
        title_en = cleaned_data['title_en']
        text_ru = cleaned_data['text_ru']
        text_en = cleaned_data['text_en']

        if (not title_ru and not text_ru) and (not title_en and not text_en):
            raise forms.ValidationError("Need to fill 'Title ru' or 'Title en'")

        if not title_ru and text_ru:
            self._errors['title_ru'] = self.error_class(["Need to fill 'Title ru'"])
            del cleaned_data['title_ru']

        if not title_en and text_en:
            self._errors['title_en'] = self.error_class(["Need to fill 'Title en'"])
            del cleaned_data['title_en']

        return cleaned_data


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleForm
    save_on_top = True
    list_display = ('slug', 'title', 'is_published', 'published')
    list_filter = (('published', TimedBooleanFilter), )
    search_fields = ('slug', 'title_ru', 'title_en', 'text_ru', 'text_en', 'categories__slug', 'categories__title_ru', 'categories__title_en', )
    ordering = ('-published', )
    inlines = (ArticleUploadInlineAdmin, )

    fields = ('slug', 'title_ru', 'text_ru', 'title_en', 'text_en', 'categories', 'tags', 'comments_hidden', 'published', )
    filter_horizontal = ('categories', 'tags', )

    def is_published(self, obj):
        return bool(obj.published)
    is_published.boolean = True


class ArticleUploadAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    save_on_top = True
    actions = (actions.make_approved, )
    list_display = ('pk', 'article', 'author_str', 'type', 'created_str', 'is_approved', )
    list_filter = (('approved', TimedBooleanFilter), )
    ordering = ('-created', )
    select_related = ('article', )
    raw_id_fields = ('author', 'article', )
    search_fields = ('article__slug', 'author__username', )

    def is_approved(self, obj):
        return bool(obj.approved)
    is_approved.boolean = True

    def created_str(self, obj):
        return obj.created.strftime('%Y-%m-%d\xc2\xa0%H:%M')
    created_str.admin_order_field = 'created'
    created_str.short_description = 'created'


admin.site.register(
    models.Category,
    list_display=('title_ru', 'title_en', 'essential', 'parent', ))
admin.site.register(
    models.Tag,
    list_display=('slug', 'title_ru', 'count_articles_ru', 'title_en', 'count_articles_en', ),
    search_fields=('title_ru', 'title_en', ))
admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.ArticleUpload, ArticleUploadAdmin)
admin.site.register(models.Comment, CommentAdmin)

# -*- coding:utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from marcus import models

def model_field(model, fieldname, **kwargs):
    return model._meta.get_field(fieldname).formfield(**kwargs)

class CommentForm(forms.Form):
    text = model_field(models.Comment, 'text', widget=forms.Textarea(attrs={'cols': '80', 'rows': '20'}))
    language = model_field(models.Comment, 'language')
    name = forms.CharField(label=_(u'Name'), required=False)

    def __init__(self, user=None, ip=None, article=None, language=None, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        if user and not user.is_authenticated():
            user = User.objects.get(username='marcus_guest')
        self.user = user
        self.ip = ip
        self.article = article
        self.initial['language'] = article.comment_language(language)
        if not article.is_bilingual() or language:
            self.fields['language'].widget = forms.HiddenInput()

    def show_language(self):
        return not self.fields['language'].widget.is_hidden

    def clean_name(self):
        if self.user.username != 'marcus_guest':
            return u''
        if not self.cleaned_data['name']:
            raise forms.ValidationError(_(u'This field is required.'))
        return self.cleaned_data['name']

    def save(self):
        return self.article.comment_set.create(
            type = 'comment',
            text = self.cleaned_data['text'],
            author = self.user,
            guest_name = self.cleaned_data['name'],
            ip = self.ip,
            language = self.cleaned_data['language'],
        )

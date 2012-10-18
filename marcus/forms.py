from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from marcus import models
from marcus.utils import get_language_code_in_text


def model_field(model, fieldname, **kwargs):
    return model._meta.get_field(fieldname).formfield(**kwargs)


class CommentForm(forms.Form):
    text = model_field(models.Comment, 'text', widget=forms.Textarea(attrs={'cols': '80', 'rows': '20'}))
    language = model_field(models.Comment, 'language', required=False)
    name = forms.CharField(label=_(u'Name or OpenID'), required=False)

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

    def clean_language(self):
        if not self.cleaned_data['language']:
            language = get_language_code_in_text(self.data.get('text', ''))
        else:
            raise forms.ValidationError(_(u'This field is required.'))
        return language

    def clean_name(self):
        if self.user.username != 'marcus_guest':
            return u''
        if not self.cleaned_data['name']:
            raise forms.ValidationError(_(u'This field is required.'))
        if User.objects.filter(username=self.cleaned_data['name']).exists():
            raise forms.ValidationError(_(u'This name is already taken.'))
        return self.cleaned_data['name']

    def save(self):
        return self.article.comment_set.create(
            type='comment',
            text=self.cleaned_data['text'],
            author=self.user,
            guest_name=self.cleaned_data['name'],
            ip=self.ip,
            language=self.cleaned_data['language'],
        )

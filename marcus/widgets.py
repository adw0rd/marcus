from django.core.urlresolvers import reverse
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe


class AdminImageWidget(AdminFileWidget):
    """
    A FileField Widget that displays an image instead of a file path
    if the current file is an image.
    """
    def render(self, name, value, attrs=None):
        output = []
        if value:
            url = value.url if hasattr(value, 'url') else value.name
            thumbnail_url = reverse('article-upload-image-preview', args=[value.instance.pk])
            output.append(
                '<a href="{url}"><img src="{thumbnail_url}" /></a><br />'
                '<tt>{url}</tt><br />'.format(url=url, thumbnail_url=thumbnail_url))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe("".join(output))

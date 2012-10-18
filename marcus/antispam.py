from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str

from scipio import antispam
from scipio.antispam import akismet
from scipio.models import Profile as ScipioProfile

from marcus import utils


class AkismetHandler(akismet.AkismetBaseHandler):
    def get_params(self, request, comment, **kwargs):
        try:
            openid = comment.author.scipio_profile.openid
        except ScipioProfile.DoesNotExist:
            openid = ''
        return {
            'blog': utils.absolute_url(reverse('marcus-index')),
            'user_ip': comment.ip,
            'permalink': utils.absolute_url(comment.get_absolute_url()),
            'comment_type': 'comment',
            'comment_author': smart_str(comment.by_guest() and comment.guest_name or comment.author),
            'comment_author_url': smart_str(openid),
            'comment_content': smart_str(comment.text),
        }


class Paranoia(object):
    def validate(self, request, **kwargs):
        return 'paranoia'

conveyor = antispam.Conveyor([
    antispam.WhitelistHandler(),
    antispam.HoneyPotHandler(),
    AkismetHandler(),
    Paranoia(),
])

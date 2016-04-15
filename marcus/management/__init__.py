from django.db.models import signals


def create_system_user(username):
    from django.contrib.auth.models import User
    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        password = User.objects.make_random_password()
        User.objects.create_user(username, username + '@localhost', password)


def init(sender, **kwargs):
    import marcus.models

    if kwargs['app_config'].models_module == marcus.models:
        create_system_user('marcus_guest')

signals.post_migrate.connect(init)

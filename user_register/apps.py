from django.apps import AppConfig


class UserRegisterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_register'

    def ready(self):
        import user_register.signals    # noqa: F401

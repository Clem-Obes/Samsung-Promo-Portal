from django.apps import AppConfig


class PromotionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'promotions'
    verbose_name = '🚀 Campaigns & Tasks'

    def ready(self):
        import promotions.signals  # noqa: F401

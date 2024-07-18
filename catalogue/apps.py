from django.apps import AppConfig


class CatalogueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalogue'

    def ready(self):
        __import__('catalogue.analytics.post_analytics')
        print("Signals are ready")
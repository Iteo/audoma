from django.apps import AppConfig


class SplitV2APIConfig(AppConfig):
    name = 'v2_api'
    verbose_name = "Split V2 API"

    def ready(self):
        from v2_api import monkey

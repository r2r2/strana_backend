from django.apps import AppConfig


class PanelManagerConfig(AppConfig):
    name = "panel_manager"
    verbose_name = "Панель менеджера"

    def ready(self):
        pass
        #from . import signals

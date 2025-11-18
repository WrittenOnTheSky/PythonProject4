# ==================== project_root/core_app.py ====================
"""
CoreApp — ядро проекта
- Управляет EventBus, PluginManager, heartbeat
- События для плагинов
- Методы системного захвата через core.capture API
"""
import pkgutil
import importlib
import core.сore_api
import threading
from core.сore_api import api

class CoreApp:
    def __init__(self, plugins_path='plugins'):
        self.plugins_path = plugins_path
        self.plugin_manager = PluginManager(self)
        self.bus = EventBus()
        self.running = False

    def start(self, heartbeat_interval=1.0):
        self.running = True
        self.bus.emit('app.start')
        while self.running:
            self.bus.emit('heartbeat')
            import time
            time.sleep(heartbeat_interval)

    def stop(self):
        self.running = False
        self.bus.emit('app.stop')

    def screen_capture(self):
        """
        Запуск захвата области экрана в отдельном потоке
        и генерация события 'screen.captured'
        """
        def worker():
            img_dict = api.image.select_area()  # {'image': PIL.Image, 'rect': (x,y,w,h)}
            if img_dict['image']:
                self.bus.emit('screen.captured', **img_dict)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

# Простейшая реализация EventBus и PluginManager (для полноты)
class EventBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_name, callback):
        self.subscribers.setdefault(event_name, []).append(callback)

    def emit(self, event_name, **kwargs):
        for callback in self.subscribers.get(event_name, []):
            callback(**kwargs)

class PluginManager:
    def __init__(self, app):
        self.app = app

    def _make_api(self):
        return api  # возвращаем CaptureAPI для плагинов

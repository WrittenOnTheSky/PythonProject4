"""
MVP CoreApp — минимальное ядро модульного десктоп-фреймворка.
Запуск: python core_app.py

Что делает:
- простой EventBus (subscribe/emit)
- PluginManager: загружает плагины из ./plugins (каждый плагин должен иметь функцию register(api))
- API, который видят плагины: api.subscribe(event, handler), api.emit(event, **kwargs), api.send_output(text)
- CLI-вывод по умолчанию
- Небольшой цикл-«heartbeat» для демонстрации событий

Плагин-шаблон (plugins/example_plugin.py):

    def register(api):
        def on_start(**kwargs):
            api.send_output("example_plugin: on_start received")
        api.subscribe('app.start', on_start)

"""

import argparse
import importlib.util
import inspect
import logging
import os
import sys
import threading
import time
from types import ModuleType
from typing import Callable, Dict, List, Any

# --- Конфигурация логирования ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger('core')

# --- EventBus ---
class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[..., None]]] = {}
        self._lock = threading.RLock()

    def subscribe(self, event: str, handler: Callable[..., None]):
        with self._lock:
            self._subscribers.setdefault(event, []).append(handler)
        logger.debug(f"Subscribed handler {handler} to event '{event}'")

    def emit(self, event: str, **kwargs) -> None:
        handlers = []
        with self._lock:
            handlers = list(self._subscribers.get(event, []))
        logger.debug(f"Emitting event '{event}' to {len(handlers)} handlers: {kwargs}")
        for h in handlers:
            try:
                h(**kwargs)
            except Exception as e:
                logger.exception(f"Error in handler for event '{event}': {e}")

# --- Plugin Manager ---
class PluginManager:
    def __init__(self, plugins_path: str, api_factory: Callable[[], Any]):
        self.plugins_path = plugins_path
        self.api_factory = api_factory
        self.plugins: Dict[str, ModuleType] = {}

    def discover_plugins(self) -> List[str]:
        if not os.path.isdir(self.plugins_path):
            logger.info("Plugins directory not found, creating: %s", self.plugins_path)
            os.makedirs(self.plugins_path, exist_ok=True)
        names = [f[:-3] for f in os.listdir(self.plugins_path) if f.endswith('.py') and not f.startswith('_')]
        logger.info(f"Discovered plugins: {names}")
        return names

    def load_plugin(self, name: str):
        path = os.path.join(self.plugins_path, f"{name}.py")
        spec = importlib.util.spec_from_file_location(f"plugins.{name}", path)
        if spec is None or spec.loader is None:
            logger.error(f"Cannot load plugin {name} (spec missing)")
            return
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)  # type: ignore
        except Exception:
            logger.exception(f"Failed to execute plugin module {name}")
            return
        # Plugin must expose register(api)
        if not hasattr(module, 'register') or not inspect.isfunction(module.register):
            logger.warning(f"Plugin {name} has no register(api) function — skipping")
            return
        api = self.api_factory()
        try:
            module.register(api)
            self.plugins[name] = module
            logger.info(f"Loaded plugin: {name}")
        except Exception:
            logger.exception(f"Error during register() of plugin {name}")

    def load_all(self):
        for name in self.discover_plugins():
            self.load_plugin(name)

# --- API to plugins ---
class PluginAPI:
    def __init__(self, event_bus: EventBus, output_callback: Callable[[str], None]):
        self._bus = event_bus
        self._output = output_callback

    def subscribe(self, event: str, handler: Callable[..., None]):
        self._bus.subscribe(event, handler)

    def emit(self, event: str, **kwargs):
        self._bus.emit(event, **kwargs)

    def send_output(self, text: str):
        self._output(text)

# --- CoreApp ---
class CoreApp:
    def __init__(self, plugins_path: str = 'plugins'):
        self.bus = EventBus()
        # output handlers: list of callables that take text
        self._outputs: List[Callable[[str], None]] = []
        self.plugins_path = plugins_path
        # plugin manager gets API factory so each plugin gets the same API instance bound to this app
        self.plugin_manager = PluginManager(plugins_path, self._make_api)
        self._running = False

    def _make_api(self) -> PluginAPI:
        return PluginAPI(self.bus, self._emit_output)

    # Output registration
    def register_output(self, output_callable: Callable[[str], None]):
        self._outputs.append(output_callable)

    def _emit_output(self, text: str):
        for out in list(self._outputs):
            try:
                out(text)
            except Exception:
                logger.exception('Error in output handler')

    def start(self, heartbeat_interval: float = 1.0):
        logger.info('Starting CoreApp')
        self._running = True
        # default output: CLI
        self.register_output(lambda t: print(t))
        # load plugins
        self.plugin_manager.load_all()
        # emit app.start
        self.bus.emit('app.start')

        # Simple heartbeat loop — демонстрация событий
        try:
            i = 0
            while self._running:
                i += 1
                self.bus.emit('app.heartbeat', count=i)
                time.sleep(heartbeat_interval)
        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt received — shutting down')
        finally:
            self.stop()

    def stop(self):
        if not self._running:
            return
        logger.info('Stopping CoreApp')
        self._running = False
        self.bus.emit('app.stop')

# --- CLI entrypoint ---
def main():
    parser = argparse.ArgumentParser(description='CoreApp (MVP core)')
    parser.add_argument('--plugins', default='plugins', help='plugins directory')
    parser.add_argument('--heartbeat', type=float, default=1.0, help='heartbeat interval seconds')
    args = parser.parse_args()

    app = CoreApp(plugins_path=args.plugins)

    # Example: attach a simple log output
    def log_output(text: str):
        logger.info(f"OUTPUT: {text}")

    app.register_output(log_output)

    # Example: subscribe a builtin handler to heartbeat for demonstration
    def heartbeat_handler(count: int = 0, **kwargs):
        # don't spam logs too often; log every 5th
        if count % 5 == 0:
            logger.info(f"Heartbeat {count}")

    app.bus.subscribe('app.heartbeat', heartbeat_handler)

    app.start(heartbeat_interval=args.heartbeat)


if __name__ == '__main__':
    main()

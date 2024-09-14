import operator

from dependency_injector import providers
from environs import Env


class ConfigEnvWrapper:
    def __init__(self, config: providers.Configuration, env: Env):
        self._config = config
        self._env = env

    def set_int(self, path: str, env: str, **kwargs):
        self._path(path).override(self._env.int(env, **kwargs))

    def set_str(self, path: str, env: str, **kwargs):
        self._path(path).override(self._env.str(env, **kwargs))

    def set_bool(self, path: str, env: str, **kwargs):
        self._path(path).override(self._env.bool(env, **kwargs))

    def set_list(self, path: str, env: str, **kwargs):
        self._path(path).override(self._env.list(env, **kwargs))

    def _path(self, path):
        return operator.attrgetter(path)(self._config)

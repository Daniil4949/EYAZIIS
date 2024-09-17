from dependency_injector import providers
from environs import Env

from .util.config import ConfigEnvWrapper


def setup_config(config: providers.Configuration):
    from app.container import dynamic

    Env.read_env()
    env = Env()
    wrapper = ConfigEnvWrapper(config, env)

    # Web server
    # ------------------------------------------------------------------------
    wrapper.set_int(
        path="server.port",
        env="SERVER_PORT",
        default=8080,
    )

    # MongoDB
    # ------------------------------------------------------------------------
    wrapper.set_str(
        path="mongo.url",
        env="MONGO_URL",
        default="mongodb://localhost:27017/test_mongo",
    )

    # MongoDB
    # ------------------------------------------------------------------------
    wrapper.set_str(
        path="open_ai.token",
        env="OPEN_AI_TOKEN",
    )

    dynamic.config = config

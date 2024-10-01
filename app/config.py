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

    # S3
    # ------------------------------------------------------------------------
    wrapper.set_str(
        path="s3.access_key_id",
        env="S3_ACCESS_KEY_ID",
    )
    wrapper.set_str(
        path="s3.access_key_secret",
        env="S3_ACCESS_KEY_SECRET",
    )
    wrapper.set_str(
        path="s3.region_name",
        env="S3_REGION",
    )
    wrapper.set_str(
        path="s3.endpoint",
        env="S3_ENDPOINT",
    )
    wrapper.set_str(
        path="s3.bucket",
        env="S3_BUCKET",
    )

    dynamic.config = config

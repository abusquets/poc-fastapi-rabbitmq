import logging.config
import os

import yaml


APP_ENV = os.getenv('APP_ENV', 'dev')


def setup_logging() -> None:
    path = f'logging.{APP_ENV}.yaml'
    with open(path, 'rt', encoding='utf-8') as file:
        config = yaml.safe_load(file.read())
        logging.config.dictConfig(config)

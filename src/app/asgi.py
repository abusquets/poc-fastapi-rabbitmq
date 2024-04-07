from contextlib import asynccontextmanager
import logging
from typing import AsyncIterator

from fastapi import FastAPI, Request, Response
from faststream.rabbit import RabbitBroker

from app.setup_logging import setup_logging
from shared.exceptions import APPExceptionError


setup_logging()

logger = logging.getLogger(__name__)


broker = RabbitBroker('amqp://admin:1234@rabbit:5672/test')


@broker.subscriber('test')
async def base_handler(body: str) -> None:
    logger.info(body)


async def start_broker() -> None:
    await broker.start()


async def stop_broker() -> None:
    await broker.close()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator:
    await start_broker()
    yield
    await stop_broker()


app = FastAPI(debug=True, lifespan=lifespan)


@app.get('/')
async def root() -> dict:
    return {'message': 'Hello root!'}


@app.get('/hello')
async def hello_http() -> dict:
    await broker.publish('Hello, Rabbit!', 'test')
    return {'message': 'Hello Rabbit!!'}


@app.exception_handler(APPExceptionError)
async def custom_exception_handler(_: Request, exc: APPExceptionError) -> Response:
    return Response(
        status_code=exc.status_code,
        content={'error': {'code': exc.code, 'message': exc.message}},
    )

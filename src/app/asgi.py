from contextlib import asynccontextmanager
import logging
from typing import AsyncIterator
import uuid

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from faststream.rabbit import RabbitBroker
from faststream.rabbit.annotations import RabbitMessage

from app.connection_manager import ConnectionManager
from app.schemas import BCMessageDTO, ResponseDTO, SendMessageDTO
from app.setup_logging import setup_logging
from shared.exceptions import APPExceptionError


setup_logging()

logger = logging.getLogger(__name__)

manager = ConnectionManager()

broker = RabbitBroker('amqp://admin:1234@rabbit:5672/test')


@broker.subscriber('test', retry=False)
async def base_handler(body: str, msg: RabbitMessage) -> None:
    logger.info(body)
    await manager.broadcast(BCMessageDTO(id=str(uuid.uuid4()), content=body))
    logger.info('Message send to all clients', extra={'content': body})
    await msg.ack()


async def start_broker() -> None:
    await broker.start()


async def stop_broker() -> None:
    await broker.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    await start_broker()
    app.state.broker = broker
    yield
    await stop_broker()


app = FastAPI(debug=True, lifespan=lifespan)


@app.get('/api', response_model=ResponseDTO)
async def root() -> dict:
    return {'message': 'Hello root!'}


@app.get('/api/hello', response_model=ResponseDTO)
async def hello_http(request: Request) -> dict:
    await request.app.state.broker.publish('Hello, Rabbit!', 'test')
    return {'message': 'Hello Rabbit!!'}


@app.post('/api/send-message', response_model=ResponseDTO)
async def send_message(request: Request, message: SendMessageDTO) -> dict:
    await request.app.state.broker.publish(message.content, 'test')
    return {'message': 'Message sent to RabbitMQ!'}


@app.websocket('/api/ws/{client_id}')
async def websocket_endpoint(websocket: WebSocket, client_id: int) -> None:
    logger.info(f'Client ID: {client_id}')
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.exception_handler(APPExceptionError)
async def custom_exception_handler(_: Request, exc: APPExceptionError) -> Response:
    return Response(
        status_code=exc.status_code,
        content={'error': {'code': exc.code, 'message': exc.message}},
    )

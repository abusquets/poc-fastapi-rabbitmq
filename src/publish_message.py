import logging
import os

from kombu import Connection, Exchange, Producer


logger = logging.getLogger(__name__)


url = os.getenv('RABBITMQ_URL', 'amqp://localhost:5672//')

logger.info(f'Connecting to [{url}]')


with Connection(
    url,
    userid=os.getenv('RABBITMQ_USER', 'admin'),
    password=os.getenv('RABBITMQ_PASSWORD', 'admin'),
    connect_retry=True,
) as connection:
    channel = connection.channel()
    task_exchange = Exchange('stuff', type='direct', delivery_mode='persistent')
    producer = Producer(exchange=task_exchange, channel=channel, routing_key='stuff')

    for i in range(5):
        producer.publish('{"name": "Ola k ase!!!", "n": %s}' % i, errback=lambda: logger.error('An error occured!'))

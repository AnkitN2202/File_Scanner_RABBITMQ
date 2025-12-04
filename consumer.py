
#!/usr/bin/env python3
"""
consumer.py
Simple consumer that prints messages and acknowledges them.
"""

import pika
import json
import logging
import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def consume_messages(queue_name):
    creds = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=config.RABBITMQ_HOST,
        port=config.RABBITMQ_PORT,
        credentials=creds,
        heartbeat=60,
    )
    conn = pika.BlockingConnection(params)
    channel = conn.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    # Do not give more than one unacknowledged message to a worker
    try:
        channel.basic_qos(prefetch_count=1)
    except Exception:
        # Not critical if qos cannot be set on older clients
        pass

    def callback(ch, method, properties, body):
        try:
            msg = json.loads(body)
        except Exception:
            logger.warning("Received non-json message or decode error.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print("Received:", msg, flush=True)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    logger.info(
        "Listening to queue '%s' on %s:%d. Press Ctrl+C to exit.",
        queue_name,
        config.RABBITMQ_HOST,
        config.RABBITMQ_PORT,
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Exiting...")
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    consume_messages(config.QUEUE_NAME)

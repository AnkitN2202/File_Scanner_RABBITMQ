#!/usr/bin/env python3
"""
consumer.py
Simple consumer that prints messages and acknowledges them.
"""

import pika
import json
import config


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

    def callback(ch, method, properties, body):
        msg = json.loads(body)
        print("Received:", msg, flush=True)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    print(
        f"Listening to queue '{queue_name}' on {config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}. Press Ctrl+C to exit.",
        flush=True,
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Exiting...", flush=True)
        conn.close()


if __name__ == "__main__":
    consume_messages(config.QUEUE_NAME)

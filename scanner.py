# scanner.py

import os
import json
import time
import argparse
from datetime import datetime

import pika
from tqdm import tqdm

import config


# Helper Functions
def make_connection(host, port, user, password, retries=5, backoff=2.0):
    creds = pika.PlainCredentials(user, password)
    params = pika.ConnectionParameters(
        host=host, port=port, credentials=creds, heartbeat=60
    )
    attempt = 0
    while True:
        attempt += 1
        try:
            conn = pika.BlockingConnection(params)
            return conn
        except Exception as e:
            if attempt >= retries:
                raise
            wait = backoff**attempt
            print(f"Connection failed (attempt {attempt}). Retrying in {wait:.1f}s...")
            time.sleep(wait)


# create a JSON serializable message for a file path
def make_message(path):
    try:
        st = os.stat(path)
        return {
            "file_name": os.path.basename(path),
            "file_path": os.path.abspath(path),
            "size_bytes": st.st_size,
            "last_modified": datetime.fromtimestamp(st.st_mtime).isoformat(),
            "discovered_at": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        return {
            "file_name": os.path.basename(path),
            "file_path": os.path.abspath(path),
            "error": str(e),
        }


# publish one message with retry logic
def publish_message(channel, queue_name, payload, retry=3):
    body = json.dumps(payload).encode("utf-8")
    props = pika.BasicProperties(
        delivery_mode=2, content_type="application/json"
    )  # persistent
    attempt = 0
    while True:
        attempt += 1
        try:
            channel.basic_publish(
                exchange="", routing_key=queue_name, body=body, properties=props
            )
            return True
        except Exception as e:
            if attempt >= retry:
                print(f"Failed to publish after {attempt} attempts: {e}")
                return False
            wait = 2**attempt
            print(f"Publish failed, retrying in {wait}s (attempt {attempt})...")
            time.sleep(wait)


# main scanner
def scan_and_publish(
    root_path,
    host,
    port,
    user,
    password,
    queue_name,
    show_progress=False,
    ext_filter=None,
):
    # connect
    conn = make_connection(host, port, user, password)
    channel = conn.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    # backup folder for offline processing
    backup_dir = os.path.join(os.getcwd(), "backup_json")
    os.makedirs(backup_dir, exist_ok=True)

    sent = 0
    pbar = (
        tqdm(total=0, desc="Publishing files", unit="file", dynamic_ncols=True)
        if show_progress
        else None
    )

    # walk directory without storing all files
    for root, dirs, filenames in os.walk(root_path):
        for f in filenames:
            if ext_filter:
                _, ext = os.path.splitext(f)
                if ext.lower() not in ext_filter:
                    continue
            path = os.path.join(root, f)
            msg = make_message(path)

            # Save local backup
            backup_path = os.path.join(backup_dir, f"{os.path.basename(path)}.json")
            with open(backup_path, "w") as bf:
                json.dump(msg, bf, indent=2)

            # Publish to RabbitMQ
            ok = publish_message(channel, queue_name, msg)
            if not ok:
                print("Warning: message failed for", path)
            else:
                sent += 1

            if pbar:
                pbar.update(1)

    if pbar:
        pbar.close()

    conn.close()
    print(
        f"Done. Published {sent} messages to queue '{queue_name}' and saved backup locally."
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        sys.argv += ["/Users/ankitsandeepnanaware/Documents"]  # default folder to scan

    ap = argparse.ArgumentParser(
        description="Simple scanner -> RabbitMQ + local backup"
    )
    ap.add_argument("path", help="Root directory to scan")
    ap.add_argument("--host", default=config.RABBITMQ_HOST)
    ap.add_argument("--port", type=int, default=config.RABBITMQ_PORT)
    ap.add_argument("--user", default=config.RABBITMQ_USER)
    ap.add_argument("--password", default=config.RABBITMQ_PASS)
    ap.add_argument("--queue", default=config.QUEUE_NAME)
    ap.add_argument("--progress", action="store_true", help="Show progress bar")
    ap.add_argument(
        "--ext",
        default=None,
        help="Comma-separated extensions to include, e.g. .txt,.csv",
    )

    args = ap.parse_args()
    ext_set = (
        {
            e.strip().lower() if e.strip().startswith(".") else f".{e.strip().lower()}"
            for e in args.ext.split(",")
        }
        if args.ext
        else None
    )

    scan_and_publish(
        root_path=args.path,
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        queue_name=args.queue,
        show_progress=args.progress,
        ext_filter=ext_set,
    )

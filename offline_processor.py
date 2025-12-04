#!/usr/bin/env python3
"""
offline_processor.py
Process locally backed-up JSON messages without RabbitMQ.
"""

import json
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

backup_dir = os.path.join(os.getcwd(), "backup_json")

if not os.path.exists(backup_dir):
    print("No backup found!")
else:
    files = sorted(os.listdir(backup_dir))
    for file in files:
        if file.endswith(".json"):
            path = os.path.join(backup_dir, file)
            try:
                with open(path, encoding="utf-8") as f:
                    msg = json.load(f)
                    print("Offline message:", msg)
            except json.JSONDecodeError:
                logger.warning("Skipping invalid JSON file: %s", path)
            except Exception as e:
                logger.warning("Failed to read %s: %s", path, e)

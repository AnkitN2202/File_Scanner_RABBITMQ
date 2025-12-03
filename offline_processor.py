#!/usr/bin/env python3
"""
offline_processor.py
Process locally backed-up JSON messages without RabbitMQ.
"""

import json
import os

backup_dir = os.path.join(os.getcwd(), "backup_json")

if not os.path.exists(backup_dir):
    print("No backup found!")
else:
    for file in os.listdir(backup_dir):
        if file.endswith(".json"):
            with open(os.path.join(backup_dir, file)) as f:
                msg = json.load(f)
                print("Offline message:", msg)

# File Scanner → RabbitMQ + Offline Backup

## Overview
This project recursively scans a local file system, generates metadata for each file, and publishes messages to a RabbitMQ queue. All messages are also backed up locally in JSON format to allow offline processing.

The solution includes three scripts:
1. `scanner.py` - Main scanner that publishes messages and saves local backups.
2. `consumer.py` - Simple RabbitMQ consumer that prints and acknowledges messages.
3. `offline_processor.py` - Processes locally backed-up JSON messages without RabbitMQ.

---

## Features
- Recursive directory scanning with optional file extension filter.
- JSON message creation with file metadata:
  - File name, path, size, last modified, discovery timestamp.
- Robust RabbitMQ integration with retry logic for connection and publishing.
- Local JSON backup for offline processing.
- Progress bar support for large directory structures.

---

## Requirements
- Python 3.8+
- RabbitMQ server (local or remote)
- Python libraries:
  ```bash
  pip install pika tqdm

## Configuration
Edit config.py to set your RabbitMQ connection details:
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "guest"
RABBITMQ_PASS = "guest"
QUEUE_NAME = "file_queue"


## How to run
1. Scanner
Recursively scans directories and publishes messages:
python scanner.py /path/to/scan --progress --ext .txt,.csv

Options:
path – Root directory to scan.
--progress – Show progress bar.
--ext – Comma-separated extensions to include (optional).

Example:
python scanner.py ~/Documents --progress --ext .txt,.pdf

This will:
Publish messages to RabbitMQ.
Save a backup JSON file for each scanned file in backup_json/.

2. Consumer
Listen to the RabbitMQ queue and print messages:
python consumer.py

Check messages in RabbitMQ visually by logging into the RabbitMQ management UI:
http://localhost:15672
Username: guest
Password: guest

3. Offline Processor
Process locally backed-up JSON files without RabbitMQ:
python offline_processor.py
This prints all saved messages from backup_json/.

- The scanner is robust for large directories using streaming rather than loading all files at once.
- RabbitMQ messages are persistent to ensure reliability.
- Retry logic is implemented for both connection and message publishing.

## Directory Structure
file-scanner-rabbitmq/
├── scanner.py
├── consumer.py
├── offline_processor.py
├── config.py
├── backup_json/   # automatically created for offline backup
├── README.md

## Example Output

- Scanner:
Publishing files: 100%|██████████| 50/50 [00:05<00:00,  9.5file/s]
Done. Published 50 messages to queue 'file_queue' and saved backup locally.

- Consumer:
Received: {'file_name': 'example.txt', 'file_path': '/Users/username/Documents/example.txt', 'size_bytes': 123, ...}

- Offline Processor:
Offline message: {'file_name': 'example.txt', 'file_path': '/Users/username/Documents/example.txt', 'size_bytes': 123, ...}

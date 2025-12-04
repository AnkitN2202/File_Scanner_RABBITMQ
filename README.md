# File Scanner → RabbitMQ + Offline Backup

## Overview
This project scans a directory, collects metadata for each file, and sends it to a RabbitMQ queue.  
Each message is also saved locally as a JSON file so the data can be processed offline if RabbitMQ is not available.

The project includes three scripts:

1. `scanner.py` — scans files, publishes messages, and writes JSON backups.  
2. `consumer.py` — listens to the queue and prints messages.  
3. `offline_processor.py` — reads all locally saved messages from `backup_json/`.

---

## Features
- Recursive directory scanning with optional file-extension filtering.  
- JSON metadata for each file:
  - file name  
  - file path  
  - size in bytes  
  - last modified timestamp  
  - discovery timestamp  
- RabbitMQ publishing with retry logic.  
- Local JSON backups for offline processing.  
- Optional progress bar for large file trees.  
- Works on large directories because files are processed one-by-one instead of preloading everything.

---

## Requirements
- Python 3.8+  
- RabbitMQ server (local install or Docker)  
- Python libraries:
  ```bash
  pip install pika tqdm


## Configuration
Edit config.py to set your RabbitMQ connection details:
`RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "guest"
RABBITMQ_PASS = "guest"
QUEUE_NAME = "file_queue"`

## Running RabbitMQ with Docker:
If you use Docker Desktop, you can  start RabbitMQ with:

`docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management`
  
## RabbitMQ Management UI:

`http://localhost:15672
Username: guest
Password: guest`

Your Python scripts will connect automatically as long as RABBITMQ_HOST = "localhost".

## How to run
1. Scanner
Scans files and publishes their metadata to RabbitMQ.
```python scanner.py /path/to/scan --progress --ext .txt,.csv```

Options:
- path — directory to scan
- progress — show progress bar
- ext — comma-separated extensions (optional)

Example:
`python scanner.py ~/Documents --progress --ext .txt,.pdf`

The scanner will:
- Publish metadata for each file to the queue.
- Save a backup JSON file inside backup_json/.

2. Consumer
Listen to the RabbitMQ queue and print messages:

```python consumer.py```

You can also check incoming messages in the RabbitMQ UI.

3. Offline Processor
Reads all locally stored JSON backups:

`python offline_processor.py`

This prints each saved message directly, without involving RabbitMQ.

## Queue Behavior:
During scanning, the queue may show temporary spikes.
This happens because the scanner publishes messages faster than the consumer processes them.
The queue then drains once the consumer catches up.
This is normal behavior for a producer-consumer workflow.

<img width="661" height="317" alt="screenshot" src="https://github.com/user-attachments/assets/f2080f03-7bf8-4337-9f37-527ba177cb55" />



- The scanner is robust for large directories using streaming rather than loading all files at once.
- RabbitMQ messages are persistent to ensure reliability.
- Retry logic is implemented for both connection and message publishing.

## Directory Structure
`file-scanner-rabbitmq/
├── scanner.py
├── consumer.py
├── offline_processor.py
├── config.py
├── backup_json/   # automatically created for offline backup
├── README.md`

## Example Output

- Scanner:
`Publishing files: 100%|██████████| 50/50 [00:05<00:00,  9.5file/s]
Done. Published 50 messages to queue 'file_queue' and saved backup locally.`

- Consumer:
`Received: {'file_name': 'example.txt', 'file_path': '/Users/username/Documents/example.txt', 'size_bytes': 123, ...}`

- Offline Processor:
`Offline message: {'file_name': 'example.txt', 'file_path': '/Users/username/Documents/example.txt', 'size_bytes': 123, ...}`


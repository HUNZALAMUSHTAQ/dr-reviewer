# Celery Worker Setup

This project has been configured with Celery for asynchronous task processing.

## Prerequisites

1. **Install Redis** (required as message broker):
   - Windows: Download from https://redis.io/download
   - Linux: `sudo apt-get install redis-server`
   - macOS: `brew install redis`

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Starting the Celery Worker

### Method 1: Using Django Management Command
```bash
python manage.py start_celery_worker
```

Options:
- `--loglevel=info` (default): Set log level (debug, info, warning, error)
- `--concurrency=1` (default): Number of worker processes

Example:
```bash
python manage.py start_celery_worker --loglevel=debug --concurrency=2
```

### Method 2: Direct Celery Command
```bash
celery -A dr_reviewer worker --loglevel=info
```

## Using Tasks

Tasks are defined in `api/tasks.py`. Here are some example tasks:

### Example Tasks Available:
- `example_task()`: Simple task that simulates work
- `process_document_task(document_id)`: Process documents
- `generate_questions_task(document_id)`: Generate questions from documents

### How to Use Tasks in Your Code:

```python
from api.tasks import example_task, process_document_task

# Call a task asynchronously
result = example_task.delay()

# Call a task with parameters
result = process_document_task.delay(document_id=123)

# Get the result (this will block until task completes)
task_result = result.get()
```

## Configuration

Celery is configured in `dr_reviewer/settings.py` with the following settings:

- **Broker**: Redis (localhost:6379/0)
- **Result Backend**: Redis (localhost:6379/0)
- **Serializer**: JSON
- **Timezone**: UTC

## Monitoring

You can monitor Celery tasks using Flower (optional):

```bash
pip install flower
celery -A dr_reviewer flower
```

Then visit http://localhost:5555 to see the web interface.

## Troubleshooting

1. **Redis Connection Error**: Make sure Redis is running
   ```bash
   redis-cli ping
   # Should return "PONG"
   ```

2. **Worker Not Starting**: Check if all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

3. **Tasks Not Executing**: Ensure the worker is running and Redis is accessible

## Development vs Production

For development, the current configuration uses:
- Local Redis instance
- Single worker process
- Info level logging

For production, consider:
- Using a production Redis instance
- Multiple worker processes
- Proper logging configuration
- Monitoring with Flower or similar tools 
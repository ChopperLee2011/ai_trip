from huey.consumer import Consumer
from task_queue.queue_config import huey
import task_queue.tasks

if __name__ == "__main__":
    consumer = Consumer(huey)
    consumer.run()
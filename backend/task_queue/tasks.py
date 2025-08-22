import json
import time
import logging
import pickle
from typing import Dict, Any
from task_queue.queue_config import huey, redis_client
from agents.travel_crew import TravelRecommendationCrew

@huey.task()
def process_travel_recommendation(task_id: str, travel_input: Dict[str, Any]):
    try:
        # redis_client.hset(f"travel:task:{task_id}", mapping={"status":"PROCESSING", "started_at": time.time()})

        logging.info(f"Task starting:  {task_id}")

        travel_crew = TravelRecommendationCrew()

        result = travel_crew.generate_recommendations(travel_input)

        redis_client.hset(f"travel:task:{task_id}", mapping={"status": "SUCCESS", "result": json.dumps(result, ensure_ascii=False, indent=2), "completed_at": time.time()})

        logging.info(f"Task completed: {task_id}")
        return result
    except Exception as e:
        redis_client.hset(f"travel:task{task_id}", mapping={"status":"FAILURE", "result": json.dumps({"error": str(e)}, ensure_ascii=False), "completed_at": time.time()})
        logging.error(f"Task failed: {task_id}, error: {str(e)}")
        raise e

def get_queue_status():
    try:
        pending_count = len(huey.pending())


        total_count = pending_count + 1
        return {
            "pending": pending_count,
            "total": total_count
        }
    except Exception as e:
        logging.error(f"Failed to get queue status: {str(e)}")
        raise e
    
def get_position(task_id: str):
    queue_key = f"huey.redis.{huey.name}"
    try:
        # TODO: 读取所有key然后反序列化去匹配id， 性能比较差
        queue_items = redis_client.lrange(queue_key, 0, -1)
        total = len(queue_items)
        position = None
        for idx, raw in enumerate(queue_items):
            message = pickle.loads(raw)
            if message.args[0] == task_id:
                position = total - idx + 1
                break
        return position

    except Exception as e:
        logging.error(f"Failed to get position: {str(e)}")
        raise e
import os
from huey import RedisHuey
from redis import Redis
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

huey = RedisHuey("trip", url=REDIS_URL)

redis_client = Redis.from_url(REDIS_URL, decode_responses=False)

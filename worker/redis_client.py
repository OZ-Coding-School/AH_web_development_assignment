import os
import time
import redis
import logging

logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


def get_redis_client(max_retries: int = 5, delay: int = 3) -> redis.Redis:
    """
    Redis 클라이언트를 생성하고 연결 검증까지 수행
    """
    for attempt in range(1, max_retries + 1):
        try:
            r = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3,
            )
            logger.info(f"Redis connected to {REDIS_HOST}:{REDIS_PORT}")
            return r
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed. (attempt {attempt}/{max_retries}): {e}")
            if attempt == max_retries:
                raise RuntimeError(f"Redis connection failed after {max_retries}retries.")
            time.sleep(delay * attempt)
        except Exception as e:
            logger.exception("Unexpected error while connecting to Redis.")
            raise e

    raise RuntimeError("Unreachable: Redis connection loop exited unexpectedly.")


redis_client = get_redis_client()

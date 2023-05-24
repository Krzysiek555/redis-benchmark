import argparse
import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from typing import Generator

import hiredis
import numpy as np
import redis


@dataclass
class Resolution:
    width: int
    height: int

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"


logger = logging.getLogger("Benchmark")


def generate_frames(count: int, res: Resolution) -> Generator[np.ndarray, None, None]:
    channels = 3
    for _ in range(count):
        yield np.ndarray(shape=(res.width, res.height, channels), dtype=np.uint8)


def push_frame(redis_client, frame_key, frame):
    logger.debug(f"Pushing {frame_key}")
    redis_client.set(frame_key, frame.tobytes())
    return frame_key


def pull_frame(redis_client: redis.Redis, frame_key: str):
    logger.debug(f"                       Pulling {frame_key}")
    pipe = redis_client.pipeline()
    pipe.get(frame_key)
    pipe.delete(frame_key)
    raw_frame, _ = pipe.execute()
    return frame_key, raw_frame


def get_redis(host: str, port: int) -> redis.Redis:
    return redis.Redis(
        host=host,
        port=port,
    )


def ingest_frames(
    frames_count: int,
    res: Resolution,
    frames_stream: Queue,
    redis_host: str,
    redis_port: int,
) -> None:
    redis_client = get_redis(redis_host, redis_port)
    redis_client.ping()
    executor = ThreadPoolExecutor(max_workers=4)
    t0 = time.monotonic()
    for idx, frame in enumerate(generate_frames(frames_count, res)):
        frame_key = f"frame-{idx}"
        future: Future = executor.submit(push_frame, redis_client, frame_key, frame)
        frames_stream.put(future)
    executor.shutdown(wait=True)
    sec_elapsed = time.monotonic() - t0
    fps = frames_count / sec_elapsed
    logger.info(
        f"Pushing {frames_count} {res} frames took {sec_elapsed} seconds (FPS {fps})"
    )


def run_benchmark(
    frames_count: int,
    res: Resolution,
    redis_host: str,
    redis_port: int,
) -> None:
    redis_client = get_redis(redis_host, redis_port)
    redis_client.ping()
    redis_version = redis_client.info()["redis_version"]
    logger.info(
        f"Redis server: {redis_version}, Redis client: {redis.__version__}, "
        f"Hiredis: {hiredis.__version__}, "
        f"video resolution: {res}, frames count: {frames_count}"
    )

    # Begin async pushing frames to Redis
    frames_stream = Queue()
    ingest_thread = Thread(
        target=ingest_frames,
        args=(frames_count, res, frames_stream, redis_host, redis_port),
        daemon=True,
    )
    ingest_thread.start()

    # Begin pulling frames from Redis
    t0 = time.monotonic()
    frames_pulled = 0
    while True:
        push_future: Future = frames_stream.get(timeout=5)
        frame_key = push_future.result(timeout=5)
        raw_frame = redis_client.get(frame_key)
        frames_pulled += 1
        if frames_pulled == frames_count:
            break

    sec_elapsed = time.monotonic() - t0
    fps = frames_count / sec_elapsed
    ingest_thread.join(timeout=10)
    logger.info(
        f"Pulling {frames_count} {res} frames took {sec_elapsed} seconds (FPS {fps})"
    )


parser = argparse.ArgumentParser()
parser.add_argument("--redis-host", type=str, default="redis")
parser.add_argument("--redis-port", type=int, default=6379)
parser.add_argument("-v", "--verbose", action="store_true")

if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig()
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    frames_count_ = 200
    resolution = Resolution(width=1920, height=1080)  # Full HD
    run_benchmark(frames_count_, resolution, args.redis_host, args.redis_port)

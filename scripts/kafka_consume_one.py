#!/usr/bin/env python3
"""Consume one message from dicom.metadata.v1 and print it."""
import asyncio
import json
import os
import sys

async def main():
    from aiokafka import AIOKafkaConsumer
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
    consumer = AIOKafkaConsumer(
        "dicom.metadata.v1",
        bootstrap_servers=bootstrap,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            body = msg.value.decode("utf-8")
            try:
                obj = json.loads(body)
                print(json.dumps(obj, indent=2))
            except Exception:
                print(body)
            break
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import sys
import redis.asyncio as aioredis  # Явный чистый импорт


async def listen_telemetry():
    # Явно создаем чистый клиент прямо тут
    client = aioredis.from_url("redis://127.0.0.1:6379/0", decode_responses=True)
    pubsub = client.pubsub()
    await pubsub.subscribe("device_telemetry")

    print("🛸 Воркер AeroCode запущен и гарантированно слушает Redis...")

    async for message in pubsub.listen():
        if message["type"] == "message":
            print(f"🔥 ПОЙМАЛ КООРДИНАТЫ В WORKER.PY: {message['data']}")


if __name__ == "__main__":
    asyncio.run(listen_telemetry())

import asyncio
import random
import json
from data.db import redis_client


async def simulate_device():
    print("🤖 Скрипт-трекер запущен. Начинаю отправку координат взгляда...")

    while True:
        # Имитируем координаты X и Y на экране
        telemetry_data = {
            "x": random.randint(100, 105),  # Имитируем микро-дрожание вокруг точки 100
            "y": random.randint(500, 505)  # Имитируем микро-дрожание вокруг точки 500
        }

        # Переводим словарь в строку JSON, так как Redis умеет пересылать только строки/байты
        json_payload = json.dumps(telemetry_data)

        # Отправляем сообщение в канал (Redis создаст его на лету, если воркер еще не запущен)
        await redis_client.publish("device_telemetry", json_payload)

        print(f"Отправлено: {json_payload}")
        await asyncio.sleep(0.5)  # Шлем пакеты дважды в секунду для теста


if __name__ == "__main__":
    asyncio.run(simulate_device())
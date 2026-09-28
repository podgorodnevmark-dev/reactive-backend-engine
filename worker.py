import asyncio
import sys
from functools import wraps
import json
import math
import redis.asyncio as aioredis


# 1. Асинхронный декоратор фильтрации шума телеметрии
def filter_noise(threshold_pixels: float = 5.0):
    def decorator(func):
        # Храним последнее валидное состояние в замыкании (памяти декоратора)
        last_x = None
        last_y = None

        @wraps(func)
        async def wrapper(raw_json_string: str, *args, **kwargs):
            nonlocal last_x, last_y

            try:
                # Парсим прилетевшую из Redis строку в JSON-словарь
                coordinates = json.loads(raw_json_string)
                current_x = float(coordinates["x"])
                current_y = float(coordinates["y"])
            except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                # Если пакет битый — тихо выходим, не ломая воркер
                return None

            # Холодный старт: для самого первого пакета сессии
            if last_x is None or last_y is None:
                last_x, last_y = current_x, current_y
                return await func(coordinates, *args, **kwargs)

                # Навечно успокаиваем PyCharm: доказываем, что None исключен
            assert last_x is not None and last_y is not None

            # Вычисляем расстояние между прошлой и текущей точкой за O(1)
            distance = math.hypot(current_x - last_x, current_y - last_y)

            # Если движение меньше порога — это микродрожание (шум). Срезаем выполнение!
            if distance < threshold_pixels:
                return None

            # Если движение значительное — обновляем вечную память и пускаем в работу
            last_x, last_y = current_x, current_y
            return await func(coordinates, *args, **kwargs)

        return wrapper

    return decorator


# 2. Функция обработки команд (PyCharm больше не ругается на пропущенный аргумент 'y')
@filter_noise(threshold_pixels=4.0)
async def process_command(coords: dict):
    # Эта логика выполнится ТОЛЬКО если движение превысило порог
    x = coords["x"]
    y = coords["y"]
    print(f"🎯 Движение подтверждено! Координаты отправлены в пайплайн: X={x}, Y={y}")


# 3. Чистая функция бесконечного прослушивания очереди Redis
async def listen_telemetry():
    # Подключаемся к нашему Docker-контейнеру Redis
    client = aioredis.from_url("redis://127.0.0.1:6379/0", decode_responses=True)
    pubsub = client.pubsub()
    await pubsub.subscribe("device_telemetry")

    print("🛸 Воркер AeroCode запущен и гарантированно слушает Redis...")
    print("Ожидаю поток координат от hands-free устройства...")

    try:
        async for message in pubsub.listen():
            # Отсекаем служебные пакеты Redis на дальних подступах до декоратора
            if message["type"] == "message":
                # Передаем в задекорированную функцию чистую строку данных
                await process_command(message["data"])

    except asyncio.CancelledError:
        print("Получен сигнал остановки воркера. Закрываю сетевые соединения...")
    finally:
        await pubsub.unsubscribe("device_telemetry")
        print("Воркер успешно очистил ресурсы и остановлен.")


if __name__ == "__main__":
    try:
        asyncio.run(listen_telemetry())
    except KeyboardInterrupt:
        print("\nВоркер выключен пользователем через Ctrl+C.")
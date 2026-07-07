#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
📁 ФАЙЛ: main.py
📝 ОПИСАНИЕ: Запускатор веб-сервиса "Генератор отмазок"
═══════════════════════════════════════════════════════════════════

✅ Читает API-ключ из переменной окружения OPENAI_API_KEY
✅ Инициализирует LLM клиент и ExcuseService
✅ Монтирует статические файлы
✅ Запускает FastAPI сервер на порту 8000

═══════════════════════════════════════════════════════════════════
🚀 ЗАПУСК:
    $env:OPENAI_API_KEY="sk-proj-..."
    pip install -r requirements.txt
    python main.py
═══════════════════════════════════════════════════════════════════
"""
import os
import sys
import logging
import uvicorn
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger("Main")


def main():
    """Главная функция запуска"""
    logger.info("🎭 Запуск 'Генератора отмазок'...")

    # 1. Читаем API-ключ из переменной окружения
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        logger.error("❌ OPENAI_API_KEY не найден в переменных окружения!")
        logger.error("💡 Установите ключ командой:")
        logger.error('   $env:OPENAI_API_KEY="sk-proj-..."')
        sys.exit(1)

    logger.info("✅ API-ключ найден")

    # 2. Импортируем и инициализируем LLM клиент
    from llm_client import LLMClient

    logger.info("🤖 Инициализация LLM клиента...")
    llm_client = LLMClient(api_key=api_key, model="gpt-4.1-mini")

    # 3. Инициализируем ExcuseService
    from excuse_service import ExcuseService

    logger.info("🎭 Инициализация ExcuseService...")
    excuse_service = ExcuseService(llm_client=llm_client, history_size=10)

    # 4. Передаём сервис в app.py
    import app as app_module
    app_module.excuse_service = excuse_service

    # 5. Монтируем статические файлы
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app_module.app.mount("/static", StaticFiles(directory=static_dir), name="static")
        logger.info(f"📁 Статические файлы: {static_dir}")
    else:
        logger.warning(f"⚠️ Папка static не найдена: {static_dir}")

    # 6. Запускаем сервер
    logger.info("🚀 Запуск веб-сервера на http://localhost:8000")
    logger.info("📖 Откройте браузер и перейдите по адресу выше")

    uvicorn.run(app_module.app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
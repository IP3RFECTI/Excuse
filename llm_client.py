#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
📁 ФАЙЛ: llm_client.py
📝 ОПИСАНИЕ: Упрощённый клиент для работы с OpenAI ChatGPT API
═══════════════════════════════════════════════════════════════════

✅ Базовый вызов chat.completions API
✅ Логирование использования токенов в tokens/
✅ Без суммаризации (не нужна для генерации отмазок)
✅ Поддержка любой модели OpenAI

═══════════════════════════════════════════════════════════════════
"""
import json
import logging
from datetime import datetime
from pathlib import Path

from openai import OpenAI

logger = logging.getLogger("LLMClient")

# Пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
TOKENS_DIR = BASE_DIR / "tokens"
TOKENS_DIR.mkdir(exist_ok=True)


class TokenLogger:
    """Пишет логи использования токенов в tokens/usage_YYYY-MM-DD.jsonl"""

    def __init__(self, tokens_dir: Path):
        self.tokens_dir = tokens_dir
        self.tokens_dir.mkdir(exist_ok=True)
        self.session_total_tokens = 0
        self.session_requests = 0

    def log(self, prompt_tokens: int, completion_tokens: int, total_tokens: int, model: str) -> None:
        """Записывает одну строку в jsonl-лог"""
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }

        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = self.tokens_dir / f"usage_{date_str}.jsonl"

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning(f"Не удалось записать лог токенов: {e}")

        self.session_total_tokens += total_tokens
        self.session_requests += 1


class LLMClient:
    """Клиент для работы с ChatGPT через Chat Completions API"""

    def __init__(self, api_key: str, model: str = "gpt-4.1-mini"):
        """
        Инициализация клиента.

        :param api_key: API-ключ OpenAI
        :param model: Модель по умолчанию
        """
        if not api_key:
            raise ValueError("❌ API-ключ не предоставлен!")

        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.token_logger = TokenLogger(TOKENS_DIR)

        logger.info(f"✅ LLM клиент инициализирован (модель: {self.model})")
        logger.info(f"📁 Логи токенов: {TOKENS_DIR}")

    def chat(self, user_message: str, system_prompt: str = "",
             temperature: float = 0.95, max_tokens: int = 500) -> str:
        """
        Отправляет сообщение в ChatGPT и получает ответ.

        :param user_message: Сообщение пользователя
        :param system_prompt: Системный промпт
        :param temperature: Температура генерации (0.0 - 2.0)
        :param max_tokens: Максимальное количество токенов в ответе
        :return: Ответ от модели
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_message})

            logger.debug(f"📤 Запрос к ChatGPT: {user_message[:50]}...")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            answer = response.choices[0].message.content.strip()
            usage = response.usage

            logger.debug(f"📥 Ответ получен: {len(answer)} символов")

            if usage:
                logger.info(f"📊 prompt={usage.prompt_tokens}, "
                            f"completion={usage.completion_tokens}, "
                            f"total={usage.total_tokens}")

                self.token_logger.log(
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    total_tokens=usage.total_tokens,
                    model=self.model,
                )

            return answer

        except Exception as e:
            logger.error(f"❌ Ошибка ChatGPT: {type(e).__name__}: {e}")
            return f"(Ошибка ChatGPT: {e})"
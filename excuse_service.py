#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
📁 ФАЙЛ: excuse_service.py
📝 ОПИСАНИЕ: Сервис генерации отмазок
═══════════════════════════════════════════════════════════════════

✅ Генерация креативных отмазок через LLM
✅ Оценка правдоподобности отмазок (0-100%)
✅ Хранение истории в памяти сессии (до 10 штук)
✅ Предустановленные ситуации + пользовательские

═══════════════════════════════════════════════════════════════════
"""
import re
import uuid
import logging
from typing import List, Dict
from dataclasses import dataclass, asdict
from datetime import datetime

from llm_client import LLMClient

logger = logging.getLogger("ExcuseService")


@dataclass
class Excuse:
    """Отмазка с метаданными"""
    id: str
    situation: str
    excuse_text: str
    rating: int
    timestamp: str

    def to_dict(self):
        return asdict(self)


class ExcuseService:
    """Сервис для генерации и хранения отмазок"""

    # Предустановленные ситуации
    PRESET_SITUATIONS = [
        "Опоздал на работу",
        "Не сделал домашнее задание",
        "Забыл про день рождения друга"
    ]

    def __init__(self, llm_client: LLMClient, history_size: int = 10):
        """
        Инициализация сервиса.

        :param llm_client: Клиент для работы с LLM
        :param history_size: Максимальный размер истории отмазок
        """
        self.llm = llm_client
        self.history_size = history_size
        self.history: List[Excuse] = []

        logger.info(f"✅ ExcuseService инициализирован (история: {history_size} отмазок)")

    def generate_excuse(self, situation: str, custom_text: str = "") -> Excuse:
        """
        Генерирует отмазку для ситуации.

        :param situation: Тип ситуации (из пресетов или "Другое")
        :param custom_text: Пользовательский текст ситуации (если "Другое")
        :return: Сгенерированная отмазка с рейтингом
        """
        # Определяем финальную ситуацию
        if situation == "Другое" and custom_text:
            full_situation = custom_text
        else:
            full_situation = situation

        logger.info(f"🎭 Генерация отмазки для: {full_situation}")

        # 1. Генерируем отмазку
        excuse_text = self._generate_excuse_text(full_situation)

        # 2. Оцениваем правдоподобность
        rating = self._rate_excuse(excuse_text, full_situation)

        # 3. Создаём объект отмазки
        excuse = Excuse(
            id=str(uuid.uuid4()),
            situation=full_situation,
            excuse_text=excuse_text,
            rating=rating,
            timestamp=datetime.now().isoformat(timespec="seconds")
        )

        # 4. Добавляем в историю
        self._add_to_history(excuse)

        logger.info(f"✅ Отмазка сгенерирована (рейтинг: {rating}%)")
        return excuse

    def _generate_excuse_text(self, situation: str) -> str:
        """Генерирует текст отмазки через LLM"""
        system_prompt = (
            "Ты — мастер креативных и убедительных отмазок. "
            "Придумывай правдоподобные, но интересные оправдания для различных ситуаций."
        )

        user_message = (
            f"Придумай креативную и убедительную отмазку для ситуации: {situation}.\n"
            f"Требования:\n"
            f"- На русском языке\n"
            f"- Максимум 3 предложения\n"
            f"- Должна звучать правдоподобно\n"
            f"- Может быть с юмором, но убедительной\n"
            f"Верни ТОЛЬКО текст отмазки, без пояснений."
        )

        return self.llm.chat(user_message, system_prompt, temperature=0.95, max_tokens=200)

    def _rate_excuse(self, excuse_text: str, situation: str) -> int:
        """Оценивает правдоподобность отмазки через LLM"""
        system_prompt = (
            "Ты — эксперт по оценке правдоподобности отмазок. "
            "Оценивай объективно по шкале от 0 до 100."
        )

        user_message = (
            f"Оцени правдоподобность этой отмазки по шкале от 0 до 100.\n"
            f"Ситуация: {situation}\n"
            f"Отмазка: {excuse_text}\n\n"
            f"Критерии оценки:\n"
            f"- 0-30: Совсем неправдоподобно, явно выдумано\n"
            f"- 31-60: Сомнительно, но возможно\n"
            f"- 61-80: Правдоподобно, многие поверят\n"
            f"- 81-100: Очень убедительно, сложно не поверить\n\n"
            f"Верни ТОЛЬКО число от 0 до 100, без пояснений."
        )

        response = self.llm.chat(user_message, system_prompt, temperature=0.3, max_tokens=50)

        # Парсим число из ответа
        try:
            numbers = re.findall(r'\d+', response)
            if numbers:
                rating = int(numbers[0])
                return max(0, min(100, rating))  # Ограничиваем диапазон 0-100
        except Exception as e:
            logger.warning(f"Не удалось распарсить рейтинг: {e}")

        # Если не удалось распарсить, возвращаем дефолтное значение
        return 50

    def _add_to_history(self, excuse: Excuse) -> None:
        """Добавляет отмазку в историю"""
        self.history.insert(0, excuse)  # Добавляем в начало

        # Ограничиваем размер истории
        if len(self.history) > self.history_size:
            self.history = self.history[:self.history_size]

    def get_history(self) -> List[Dict]:
        """Возвращает историю отмазок"""
        return [excuse.to_dict() for excuse in self.history]

    def clear_history(self) -> None:
        """Очищает историю отмазок"""
        self.history.clear()
        logger.info("🗑️ История отмазок очищена")
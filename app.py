#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
📁 ФАЙЛ: app.py
📝 ОПИСАНИЕ: FastAPI веб-приложение "Генератор отмазок"
═══════════════════════════════════════════════════════════════════

✅ GET  /              — главная страница (HTML)
✅ POST /generate      — генерация отмазки
✅ GET  /history       — история отмазок
✅ GET  /situations    — список ситуаций
✅ POST /clear-history — очистка истории

═══════════════════════════════════════════════════════════════════
"""
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from excuse_service import ExcuseService

logger = logging.getLogger("ExcuseWeb")

app = FastAPI(title="Генератор отмазок")

# Глобальный сервис (инициализируется в main.py)
excuse_service: Optional[ExcuseService] = None


class GenerateRequest(BaseModel):
    """Запрос на генерацию отмазки"""
    situation: str
    custom_text: str = ""


class GenerateResponse(BaseModel):
    """Ответ с сгенерированной отмазкой"""
    id: str
    situation: str
    excuse_text: str
    rating: int
    timestamp: str


@app.get("/", response_class=HTMLResponse)
async def index():
    """Главная страница"""
    html_path = Path(__file__).parent / "templates" / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="HTML template not found")

    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/generate", response_model=GenerateResponse)
async def generate_excuse(request: GenerateRequest):
    """Генерирует отмазку для ситуации"""
    if not excuse_service:
        raise HTTPException(status_code=500, detail="Service not initialized")

    try:
        excuse = excuse_service.generate_excuse(
            situation=request.situation,
            custom_text=request.custom_text
        )
        return GenerateResponse(**excuse.to_dict())
    except Exception as e:
        logger.error(f"❌ Ошибка генерации: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history():
    """Возвращает историю отмазок"""
    if not excuse_service:
        raise HTTPException(status_code=500, detail="Service not initialized")

    return {"history": excuse_service.get_history()}


@app.get("/situations")
async def get_situations():
    """Возвращает список предустановленных ситуаций"""
    return {"situations": ExcuseService.PRESET_SITUATIONS + ["Другое"]}


@app.post("/clear-history")
async def clear_history():
    """Очищает историю отмазок"""
    if not excuse_service:
        raise HTTPException(status_code=500, detail="Service not initialized")

    excuse_service.clear_history()
    return {"success": True}
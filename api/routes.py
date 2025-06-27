# KorpBot/api/routes.py (ФИНАЛЬНАЯ ЧИСТАЯ ВЕРСИЯ)

import json
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.main import get_session
from database.models import Poll, PollOption, User

# --- Базовые настройки ---
router = APIRouter()
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")


# --- Pydantic модели для валидации JSON ответов (если понадобятся) ---
class OptionOut(BaseModel):
    id: int
    option_text: str
    votes_count: int
    model_config = ConfigDict(from_attributes=True)


class PollOut(BaseModel):
    id: int
    title: str
    status: bool
    options: List[OptionOut]
    model_config = ConfigDict(from_attributes=True)


# --- Эндпоинты (маршруты) API ---

@router.get("/", response_class=HTMLResponse, summary="Показать страницу со списком всех опросов")
async def get_index_page(request: Request, session: AsyncSession = Depends(get_session)):
    """Отдает HTML-страницу со списком всех опросов, ссылающихся на свои веб-отчеты."""
    result = await session.execute(
        select(Poll).order_by(Poll.id.desc())
    )
    all_polls = result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "polls": all_polls})


@router.get("/report/{poll_id}/view", response_class=HTMLResponse, summary="Посмотреть веб-отчет по опросу")
async def get_web_report(request: Request, poll_id: int, session: AsyncSession = Depends(get_session)):
    """Генерирует и возвращает HTML-страницу с отчетом, графиком и списком проголосовавших."""
    logger.info(f"--- [ОТЧЕТ] Запрошен веб-отчет для опроса ID: {poll_id} ---")

    # 1. Получаем опрос
    poll_result = await session.execute(select(Poll).filter(Poll.id == poll_id))
    poll = poll_result.scalar_one_or_none()

    if not poll:
        logger.warning(f"[ОТЧЕТ] Опрос с ID {poll_id} не найден.")
        raise HTTPException(status_code=404, detail=f"Опрос с ID {poll_id} не найден.")
    logger.info(f"[ОТЧЕТ] Найден опрос: '{poll.title}'")

    # 2. Получаем участников с их выбором
    participants_query = select(User).options(
        selectinload(User.option)
    ).filter(User.poll_id == poll_id)
    participants_result = await session.execute(participants_query)
    participants = participants_result.scalars().all()
    logger.info(f"[ОТЧЕТ] Найдено участников в БД: {len(participants)}")

    # 3. Получаем опции для построения графика
    options_query = select(PollOption).filter(PollOption.poll_id == poll_id)
    options_result = await session.execute(options_query)
    options = options_result.scalars().all()

    # --- Подготовка данных для передачи в HTML-шаблон ---
    total_votes = len(participants)  # Самый надежный способ подсчета

    chart_labels = json.dumps([opt.option_text for opt in options] if options else [])
    chart_values = json.dumps([opt.votes_count for opt in options] if options else [])

    context = {
        "request": request,
        "poll": poll,
        "total_votes": total_votes,
        "labels": chart_labels,
        "values": chart_values,
        "participants": participants  # Передаем список участников в шаблон
    }

    return templates.TemplateResponse("report.html", context)


# --- Эндпоинты для программного взаимодействия (если нужно) ---

@router.get("/polls", response_model=List[PollOut], summary="Получить все опросы в JSON")
async def get_all_polls_json(session: AsyncSession = Depends(get_session)):
    """Возвращает JSON-список всех опросов с их опциями."""
    result = await session.execute(
        select(Poll).options(selectinload(Poll.options)).order_by(Poll.id.desc())
    )
    return result.scalars().all()


@router.get("/polls/{poll_id}", response_model=PollOut, summary="Получить конкретный опрос в JSON")
async def get_poll_by_id_json(poll_id: int, session: AsyncSession = Depends(get_session)):
    """Возвращает один опрос по его ID в формате JSON."""
    poll = await session.get(Poll, poll_id, options=[selectinload(Poll.options)])
    if not poll:
        raise HTTPException(status_code=404, detail="Опрос не найден.")
    return poll


@router.put("/polls/{poll_id}/status", summary="Изменить статус опроса")
async def update_poll_status(poll_id: int, status: bool, session: AsyncSession = Depends(get_session)):
    """Изменяет статус опроса (активный/неактивный)."""
    poll = await session.get(Poll, poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Опрос не найден.")
    poll.status = status
    await session.commit()
    return {"message": f"Статус опроса {poll_id} изменен на {status}."}
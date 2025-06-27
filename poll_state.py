# KorpBot/poll_state.py (ПОЛНАЯ ВЕРСИЯ)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import PollOption, User, Poll


async def start_new_poll(session: AsyncSession, question: str, options: list) -> int:
    """
    Создает новый опрос и добавляет его в базу данных.
    Возвращает ID созданного опроса.
    """
    try:
        new_poll = Poll(title=question)
        session.add(new_poll)
        await session.flush()

        for option_text in options:
            poll_option = PollOption(poll_id=new_poll.id, option_text=option_text, votes_count=0)
            session.add(poll_option)

        await session.commit()
        return new_poll.id
    except Exception as e:
        await session.rollback()
        print(f"Ошибка при создании опроса: {e}")
        raise


async def record_vote(session: AsyncSession, poll_id: int, option_id: int, user_tg_id: int, user_full_name: str):
    """
    Сохраняет голос пользователя за конкретный вариант опроса.
    Если пользователь уже голосовал — обновляет его голос и ФИО.
    """
    try:
        existing_vote = await session.execute(
            select(User).filter_by(poll_id=poll_id, user_tg_id=user_tg_id)
        )
        user_vote = existing_vote.scalars().first()

        if user_vote:
            # Обновляем имя на случай, если пользователь его сменил
            user_vote.user_full_name = user_full_name

            # Если пользователь сменил голос
            if user_vote.option_id != option_id:
                old_option = await session.get(PollOption, user_vote.option_id)
                if old_option and old_option.votes_count > 0:
                    old_option.votes_count -= 1

                new_option = await session.get(PollOption, option_id)
                if new_option:
                    new_option.votes_count += 1

                user_vote.option_id = option_id
        else:
            # Создаем новую запись о голосе, включая ФИО
            new_vote = User(
                poll_id=poll_id,
                user_tg_id=user_tg_id,
                option_id=option_id,
                user_full_name=user_full_name
            )
            session.add(new_vote)

            # Увеличиваем счетчик голосов
            option = await session.get(PollOption, option_id)
            if option:
                option.votes_count += 1

        await session.commit()
    except Exception as e:
        await session.rollback()
        print(f"Ошибка при сохранении голоса: {e}")
        raise
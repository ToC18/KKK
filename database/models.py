# --- START OF FILE database/models.py ---

from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs

# Используем declarative_base() вместо наследования от AsyncAttrs
# Это более современный подход в SQLAlchemy 2.0
Base = declarative_base()


class Poll(Base):
    __tablename__ = 'poll'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)
    # duration = Column(Integer) # Это поле не используется, можно раскомментировать при необходимости
    status = Column(Boolean, default=True)

    options = relationship("PollOption", back_populates="poll", cascade="all, delete-orphan")
    participants = relationship("User", back_populates="poll", cascade="all, delete-orphan")
    # Добавим связь с TelegramPoll для удобства
    telegram_map = relationship("TelegramPoll", back_populates="poll", cascade="all, delete-orphan")


class PollOption(Base):
    __tablename__ = 'poll_option'

    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey('poll.id', ondelete="CASCADE"), nullable=False)
    option_text = Column(Text, nullable=False)
    votes_count = Column(Integer, default=0)

    poll = relationship("Poll", back_populates="options")
    voters = relationship("User", back_populates="option", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey('poll.id', ondelete="CASCADE"), nullable=False)
    user_tg_id = Column(Integer, nullable=False, index=True)
    option_id = Column(Integer, ForeignKey('poll_option.id', ondelete="CASCADE"), nullable=False)

    # --- ВОТ ЭТО ПОЛЕ ДОЛЖНО БЫТЬ ---
    user_full_name = Column(String, nullable=True)

    poll = relationship("Poll", back_populates="participants")
    option = relationship("PollOption", back_populates="voters")


# --- ДОБАВЬТЕ ЭТОТ КЛАСС ---
class TelegramPoll(Base):
    __tablename__ = 'telegram_poll'

    # ID из Telegram может быть очень длинным, используем String
    telegram_poll_id = Column(String, primary_key=True)
    poll_id = Column(Integer, ForeignKey('poll.id', ondelete="CASCADE"), nullable=False)

    poll = relationship("Poll", back_populates="telegram_map")
# --- КОНЕЦ ДОБАВЛЕНИЯ ---
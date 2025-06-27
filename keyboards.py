# KorpBot/keyboards.py

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database.models import PollOption, Poll # Добавим импорты для тайп-хинтов

def get_main_menu():
    """Создает клавиатуру с основными командами."""
    buttons = [
        [KeyboardButton(text="/poll 🙋‍♂️ Голосовать")],
        [KeyboardButton(text="/help ℹ️ Помощь")],
        [KeyboardButton(text="/site 🌐 Сайт БелАЗ")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def create_poll_choice_keyboard(polls: list) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для выбора опроса."""
    buttons = []
    for poll in polls:
        # callback_data будет содержать префикс 'poll_' и ID опроса
        callback_data = f"poll_{poll.id}"
        buttons.append([InlineKeyboardButton(text=poll.title, callback_data=callback_data)])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_admin_poll_keyboard(poll) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для управления опросом."""
    status_text = "✅ Завершить" if poll.status else "▶️ Активировать"
    status_action = "deactivate" if poll.status else "activate"

    buttons = [
        [InlineKeyboardButton(text=status_text, callback_data=f"admin_poll_{status_action}_{poll.id}")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_admin_poll_keyboard(poll) -> InlineKeyboardMarkup:
    status_text = "✅ Завершить" if poll.status else "▶️ Активировать"
    status_action = "deactivate" if poll.status else "activate"

    buttons = [
        [InlineKeyboardButton(text=status_text, callback_data=f"admin_poll_{status_action}_{poll.id}")],
        # НОВАЯ КНОПКА
        [InlineKeyboardButton(text="📊 Веб-отчет", callback_data=f"admin_report_{poll.id}")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_voting_keyboard(options: list[PollOption]) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для голосования."""
    buttons = []
    for option in options:
        # callback_data будет содержать префикс 'vote_' и ID варианта ответа
        buttons.append([InlineKeyboardButton(text=option.option_text, callback_data=f"vote_{option.id}")])

    # Добавляем кнопку для обновления результатов
    buttons.append([InlineKeyboardButton(text="🔄 Обновить результаты", callback_data=f"results_{options[0].poll_id}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_results_keyboard(poll_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру только с кнопкой обновления результатов."""
    buttons = [
        [InlineKeyboardButton(text="🔄 Обновить результаты", callback_data=f"results_{poll_id}")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_admin_poll_keyboard(poll) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для управления опросом."""
    status_text = "✅ Завершить" if poll.status else "▶️ Активировать"
    status_action = "deactivate" if poll.status else "activate"

    buttons = [
        [
            InlineKeyboardButton(text=status_text, callback_data=f"admin_poll_{status_action}_{poll.id}"),
            InlineKeyboardButton(text="📊 Веб-отчет", callback_data=f"admin_report_{poll.id}")
        ],
        # НОВАЯ КНОПКА УДАЛЕНИЯ
        [
            InlineKeyboardButton(text="❌ Удалить опрос", callback_data=f"admin_delete_ask_{poll.id}")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


# НОВАЯ КЛАВИАТУРА ПОДТВЕРЖДЕНИЯ
def create_delete_confirm_keyboard(poll_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для подтверждения удаления опроса."""
    buttons = [
        [
            InlineKeyboardButton(text="🗑️ Да, удалить!", callback_data=f"admin_delete_confirm_{poll_id}"),
            InlineKeyboardButton(text="🔙 Отмена", callback_data=f"admin_delete_cancel_{poll_id}")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
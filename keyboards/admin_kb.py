from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def stadium_moderation_keyboard(stadium_id: int) -> InlineKeyboardMarkup:
    """Stadion arizasini tasdiqlash yoki rad etish tugmalari"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve:{stadium_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject:{stadium_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def feedback_reply_keyboard(feedback_id: int) -> InlineKeyboardMarkup:
    """Taklif/shikoyatga javob yozish tugmasi"""
    keyboard = [
        [InlineKeyboardButton(text="✍️ Javob yozish", callback_data=f"reply_fb:{feedback_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Admin paneli boshqaruv tugmalari"""
    keyboard = [
        [
            InlineKeyboardButton(text="⏳ Kutilayotgan arizalar", callback_data="admin_view:pending_stadiums"),
            InlineKeyboardButton(text="📬 Yangi murojaatlar", callback_data="admin_view:new_feedbacks")
        ],
        [
            InlineKeyboardButton(text="📊 Umumiy statistika", callback_data="admin_view:stats")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

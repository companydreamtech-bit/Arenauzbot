from aiogram.fsm.state import State, StatesGroup


class AdminReplyState(StatesGroup):
    reply_text = State()  # Admin javob matnini kiritish holati

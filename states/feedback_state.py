from aiogram.fsm.state import State, StatesGroup


class FeedbackForm(StatesGroup):
    feedback_type = State()  # 1-qadam: Taklif / Shikoyat / Savol
    phone = State()          # 2-qadam: Telefon raqami
    content = State()        # 3-qadam: Murojaat matni va/yoki rasmi

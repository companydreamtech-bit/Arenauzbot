from aiogram.fsm.state import State, StatesGroup


class StadiumForm(StatesGroup):
    region = State()        # 1-qadam: Viloyat tanlash
    address = State()       # 2-qadam: Aniq manzil va mo'ljal
    phone = State()         # 3-qadam: Telefon raqami
    photos = State()        # 4-qadam: Rasmlar (kamida 2 ta)
    hourly_price = State()  # 5-qadam: Soatlik narxi
    takes_deposit = State() # 6-qadam: Zaklad oladimi?
    confirm = State()       # Yakuniy tekshirish va tasdiqlash

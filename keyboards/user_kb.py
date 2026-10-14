from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi (adminlar uchun qo'shimcha Admin tugmasi bilan)"""
    keyboard = [
        [KeyboardButton(text="🏟 Stadion joylash (Ariza qoldirish)")],
        [
            KeyboardButton(text="📋 Mening arizalarim"),
            KeyboardButton(text="📝 Taklif va shikoyat yuborish")
        ],
        [KeyboardButton(text="❓ Ko'p beriladigan savollar")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="👑 Admin paneli")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Jarayonni bekor qilish klaviaturasi"""
    keyboard = [
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def phone_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni yuborish klaviaturasi (Stadion formasi uchun)"""
    keyboard = [
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def feedback_phone_keyboard() -> ReplyKeyboardMarkup:
    """Murojaat uchun telefon raqam yoki raqamsiz davom etish klaviaturasi"""
    keyboard = [
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton(text="➡️ Raqamsiz davom etish")],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def photos_keyboard(photos_count: int) -> ReplyKeyboardMarkup:
    """Rasmlarni yuklash paytidagi klaviatura"""
    buttons = []
    if photos_count >= 2:
        buttons.append([KeyboardButton(text=f"✅ Rasmlarni yakunlash ({photos_count} ta)")])
    buttons.append([KeyboardButton(text="❌ Bekor qilish")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def regions_keyboard() -> InlineKeyboardMarkup:
    """14 ta hudud (12 viloyat + Toshkent sh. + Qoraqalpog'iston R.) 2 ustunli klaviaturasi"""
    regions = [
        "Andijon viloyati", "Farg'ona viloyati",
        "Namangan viloyati", "Toshkent shahri",
        "Toshkent viloyati", "Samarqand viloyati",
        "Buxoro viloyati", "Qashqadaryo viloyati",
        "Surxondaryo viloyati", "Jizzax viloyati",
        "Sirdaryo viloyati", "Navoiy viloyati",
        "Xorazm viloyati", "Qoraqalpog'iston R."
    ]
    builder = InlineKeyboardBuilder()
    for reg in regions:
        builder.button(text=reg, callback_data=f"region:{reg}")
    builder.adjust(2)
    return builder.as_markup()


def deposit_keyboard() -> InlineKeyboardMarkup:
    """Zaklad olinishi yoki olinmasligi bo'yicha klaviatura"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Ha, zaklad olinadi", callback_data="deposit:ha"),
            InlineKeyboardButton(text="❌ Yo'q, zaklad olinmaydi", callback_data="deposit:yo'q")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def preview_keyboard() -> InlineKeyboardMarkup:
    """Arizani yakuniy tasdiqlash klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton(text="📤 Arizani tasdiqlash va yuborish", callback_data="confirm_stadium:yes")],
        [InlineKeyboardButton(text="🔄 Qaytadan to'ldirish", callback_data="confirm_stadium:restart")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="confirm_stadium:cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def feedback_type_keyboard() -> InlineKeyboardMarkup:
    """Murojaat turi klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton(text="💡 Taklif yuborish", callback_data="fb_type:Taklif")],
        [InlineKeyboardButton(text="⚠️ Shikoyat yuborish", callback_data="fb_type:Shikoyat")],
        [InlineKeyboardButton(text="❓ Savol yo'llash", callback_data="fb_type:Savol")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def faq_inline_keyboard() -> InlineKeyboardMarkup:
    """Ko'p beriladigan savollar klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton(text="🏟 Stadion joylash uchun qanday parametrlar kerak?", callback_data="faq:params")],
        [InlineKeyboardButton(text="⏳ Ariza qancha vaqtda tasdiqlanadi?", callback_data="faq:duration")],
        [InlineKeyboardButton(text="💰 Zaklad va to'lov tartibi qanday?", callback_data="faq:deposit")],
        [InlineKeyboardButton(text="📝 Taklif yoki shikoyatni qanday yuboraman?", callback_data="faq:feedback")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

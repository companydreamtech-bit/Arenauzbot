from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, GROUP_IDS
from database import add_feedback
from states.feedback_state import FeedbackForm
from keyboards.user_kb import (
    main_menu_keyboard,
    cancel_keyboard,
    feedback_phone_keyboard,
    feedback_type_keyboard
)
from keyboards.admin_kb import feedback_reply_keyboard
from handlers.stadium import normalize_phone

router = Router()


# ===================== MUROJAATNI BOSHLASH =====================

@router.message(F.text.in_(["✍️ Taklif va shikoyat", "📝 Taklif va shikoyat yuborish", "📝 Taklif va shikoyat", "✍️ Taklif va shikoyatlar"]))
async def start_feedback(message: Message, state: FSMContext):
    """Murojaat yuborish jarayonini boshlash"""
    await state.clear()
    await state.set_state(FeedbackForm.feedback_type)

    text = (
        "📝 <b>Taklif va shikoyat yuborish</b>\n\n"
        "<b>1-qadam:</b> Murojaatingiz qaysi turga tegishli?\n"
        "Quyidagi tugmalardan birini tanlang:"
    )
    await message.answer("Jarayonni bekor qilish uchun «❌ Bekor qilish» tugmasidan foydalanishingiz mumkin.", reply_markup=cancel_keyboard())
    await message.answer(text, reply_markup=feedback_type_keyboard(), parse_mode="HTML")


# ===================== 1-QADAM: TURI =====================

@router.callback_query(FeedbackForm.feedback_type, F.data.startswith("fb_type:"))
async def process_feedback_type(callback: CallbackQuery, state: FSMContext):
    fb_type = callback.data.split(":", 1)[1]
    await state.update_data(feedback_type=fb_type)
    await state.set_state(FeedbackForm.phone)

    type_emojis = {
        "Taklif": "💡 Taklif",
        "Shikoyat": "⚠️ Shikoyat",
        "Savol": "❓ Savol"
    }
    display_type = type_emojis.get(fb_type, fb_type)
    await callback.message.edit_text(f"✅ Murojaat turi: <b>{display_type}</b>", parse_mode="HTML")

    text = (
        "📞 <b>2-qadam: Telefon raqamingiz</b>\n\n"
        "Adminlarimiz siz bilan bog'lanishi uchun telefon raqamingizni qoldiring.\n"
        "Agar raqamingizni berishni xohlamasangiz, <b>«➡️ Raqamsiz davom etish»</b> tugmasini bosing:"
    )
    await callback.message.answer(text, reply_markup=feedback_phone_keyboard(), parse_mode="HTML")
    await callback.answer()


# ===================== 2-QADAM: TELEFON =====================

@router.message(FeedbackForm.phone, F.contact)
async def process_feedback_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"

    await state.update_data(phone=phone)
    await state.set_state(FeedbackForm.content)

    text = (
        f"✅ Telefon: <b>{phone}</b>\n\n"
        "✍️ <b>3-qadam: Murojaat matni</b>\n\n"
        "O'z fikr, taklif yoki shikoyatingizni batafsil yozib yuboring.\n"
        "<i>(Ixtiyoriy: matn o'rniga rasm/skrinshot va tagiga izoh yozib yuborishingiz ham mumkin)</i>:"
    )
    await message.answer(text, reply_markup=cancel_keyboard(), parse_mode="HTML")


@router.message(FeedbackForm.phone, F.text == "➡️ Raqamsiz davom etish")
async def process_feedback_skip_phone(message: Message, state: FSMContext):
    await state.update_data(phone="Ko'rsatilmagan")
    await state.set_state(FeedbackForm.content)

    text = (
        "✍️ <b>3-qadam: Murojaat matni</b>\n\n"
        "O'z fikr, taklif yoki shikoyatingizni batafsil yozib yuboring.\n"
        "<i>(Ixtiyoriy: rasm/skrinshot va tagiga izoh yozib yuborishingiz ham mumkin)</i>:"
    )
    await message.answer(text, reply_markup=cancel_keyboard(), parse_mode="HTML")


@router.message(FeedbackForm.phone, F.text)
async def process_feedback_phone_text(message: Message, state: FSMContext):
    clean_phone = normalize_phone(message.text)
    if not clean_phone:
        await message.answer(
            "⚠️ Noto'g'ri telefon formati!\n"
            "Iltimos, pastdagi tugmalardan birini bosing yoki <code>+998901234567</code> ko'rinishida yozing:",
            reply_markup=feedback_phone_keyboard(),
            parse_mode="HTML"
        )
        return

    await state.update_data(phone=clean_phone)
    await state.set_state(FeedbackForm.content)

    text = (
        f"✅ Telefon: <b>{clean_phone}</b>\n\n"
        "✍️ <b>3-qadam: Murojaat matni</b>\n\n"
        "O'z fikr, taklif yoki shikoyatingizni batafsil yozib yuboring.\n"
        "<i>(Ixtiyoriy: rasm/skrinshot va tagiga izoh yuborishingiz ham mumkin)</i>:"
    )
    await message.answer(text, reply_markup=cancel_keyboard(), parse_mode="HTML")


# ===================== 3-QADAM: MATN VA RASM =====================

@router.message(FeedbackForm.content, F.photo)
async def process_feedback_photo(message: Message, state: FSMContext, bot: Bot):
    photo_id = message.photo[-1].file_id
    caption = message.caption or "Rasm ilova qilingan (izohsiz)"
    await finish_feedback_submission(message, state, bot, content_text=caption, photo_id=photo_id)


@router.message(FeedbackForm.content, F.text)
async def process_feedback_text(message: Message, state: FSMContext, bot: Bot):
    text = message.text.strip()
    if len(text) < 5:
        await message.answer("⚠️ Iltimos, murojaat matnini to'liqroq yozing (kamida 5 ta belgi):", reply_markup=cancel_keyboard())
        return

    await finish_feedback_submission(message, state, bot, content_text=text, photo_id=None)


async def finish_feedback_submission(message: Message, state: FSMContext, bot: Bot, content_text: str, photo_id: str | None):
    """Murojaatni bazaga yozish va barcha adminlarga yuborish"""
    data = await state.get_data()
    user = message.from_user
    fb_type = data.get("feedback_type", "Taklif")
    phone = data.get("phone", "Ko'rsatilmagan")

    feedback_id = add_feedback(
        user_id=user.id,
        username=user.username,
        feedback_type=fb_type,
        phone=phone,
        text=content_text,
        photo_id=photo_id
    )

    await state.clear()

    # Foydalanuvchiga tasdiq
    user_confirm = (
        f"✅ <b>Murojaatingiz #{feedback_id} raqami bilan qabul qilindi.</b>\n\n"
        "Adminlarimiz ko'rib chiqib, albatta sizga javob berishadi.\n"
        "Fikringiz uchun tashakkur!"
    )
    await message.answer(user_confirm, reply_markup=main_menu_keyboard(is_admin=user.id in ADMIN_IDS), parse_mode="HTML")

    # Adminga yuboriladigan xabar
    admin_text = (
        f"📩 <b>YANGI MUROJAAT #{feedback_id}</b>\n\n"
        f"📌 <b>Turi:</b> {fb_type}\n"
        f"👤 <b>Yuboruvchi:</b> @{user.username or 'username_yoq'} (ID: <code>{user.id}</code>)\n"
        f"📞 <b>Telefon:</b> {phone}\n\n"
        f"💬 <b>Murojaat matni:</b>\n{content_text}"
    )

    target_chats = list(dict.fromkeys(ADMIN_IDS + GROUP_IDS))
    for chat_id in target_chats:
        try:
            if photo_id:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_id,
                    caption=admin_text,
                    reply_markup=feedback_reply_keyboard(feedback_id),
                    parse_mode="HTML"
                )
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text=admin_text,
                    reply_markup=feedback_reply_keyboard(feedback_id),
                    parse_mode="HTML"
                )
        except Exception:
            pass

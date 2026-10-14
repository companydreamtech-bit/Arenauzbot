import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from database import get_feedback
from states.admin_state import AdminReplyState
from keyboards.user_kb import main_menu_keyboard, faq_inline_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject = None):
    """Start buyrug'i: FSM holatini tozalab, foydalanuvchiga asosiy menyuni taqdim etadi"""
    await state.clear()

    # Deep linking orqali murojaatga javob yozish (masalan: /start reply_15)
    if command and command.args and command.args.startswith("reply_"):
        if message.from_user.id in ADMIN_IDS:
            try:
                feedback_id = int(command.args.split("_")[1])
                fb = get_feedback(feedback_id)
                if fb:
                    await state.update_data(reply_feedback_id=feedback_id)
                    await state.set_state(AdminReplyState.reply_text)
                    prompt = (
                        f"✍️ <b>#{feedback_id}-sonli murojaatga javob yozing:</b>\n\n"
                        f"📌 <b>Turi:</b> {fb['feedback_type']}\n"
                        f"👤 <b>Foydalanuvchi:</b> @{fb.get('username') or 'yoq'} (ID: <code>{fb['user_id']}</code>)\n"
                        f"💬 <b>Matn:</b> <i>«{fb['text'][:300]}»</i>\n\n"
                        "Javobingizni shu yerga yozing. Bekor qilish uchun <code>❌ Bekor qilish</code> deb yozing."
                    )
                    await message.answer(prompt, parse_mode="HTML")
                    return
            except Exception:
                pass

    user_is_admin = message.from_user.id in ADMIN_IDS
    first_name = message.from_user.first_name or "Foydalanuvchi"
    text = (
        f"Assalomu alaykum, hurmatli <b>{first_name}</b>!\n\n"
        f"🏟 <b>Arenauz botiga xush kelibsiz!</b>\n\n"
        f"Ushbu bot orqali siz:\n"
        f"▫️ Stadioningizni botga joylashtirishingiz;\n"
        f"▫️ Yuborgan arizalaringiz holatini ko'rishingiz;\n"
        f"▫️ Taklif va shikoyatlaringizni adminlarga yo'llashingiz mumkin.\n\n"
        f"Quyidagi bo'limlardan birini tanlang:"
    )
    await message.answer(text, reply_markup=main_menu_keyboard(is_admin=user_is_admin), parse_mode="HTML")


@router.message(F.text == "❌ Bekor qilish")
@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Har qanday jarayonni bekor qilish va asosiy menyuga qaytish"""
    user_is_admin = message.from_user.id in ADMIN_IDS
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await message.answer(
            "❌ <b>Joriy jarayon bekor qilindi.</b>\nAsosiy menyuga qaytdingiz.",
            reply_markup=main_menu_keyboard(is_admin=user_is_admin),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "Siz asosiy menyudasiz. Kerakli bo'limni tanlang:",
            reply_markup=main_menu_keyboard(is_admin=user_is_admin)
        )


@router.message(F.text.in_(["❓ Ko'p beriladigan savollar", "Ko'p beriladigan savollar", "❓ FAQ", "ℹ️ Ko'p beriladigan savollar"]))
async def show_faq_menu(message: Message):
    """Ko'p beriladigan savollar ro'yxatini ko'rsatish"""
    text = (
        "❓ <b>Ko'p beriladigan savollar (FAQ)</b>\n\n"
        "Quyidagi tugmalardan birini tanlab, qiziqtirgan savolingizga tezkor javob oling:"
    )
    await message.answer(text, reply_markup=faq_inline_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("faq:"))
async def handle_faq_callbacks(callback: CallbackQuery):
    """FAQ tugmalari bosilganda aniq javoblar berish"""
    faq_type = callback.data.split(":")[1]

    if faq_type == "params":
        answer = (
            "🏟 <b>Stadion joylash uchun talab qilinadigan 6 ta parametr:</b>\n\n"
            "1️⃣ <b>Viloyat</b> — stadion joylashgan hudud (14 ta hududdan biri);\n"
            "2️⃣ <b>Aniq manzil</b> — ko'cha, stadion nomi va mo'ljal;\n"
            "3️⃣ <b>Telefon raqam</b> — mijozlar bog'lanishi uchun mas'ul shaxs raqami;\n"
            "4️⃣ <b>Rasmlar</b> — stadionning kamida 2 ta sifatli rasmi (maydon, kiyinish xonasi va h.k.);\n"
            "5️⃣ <b>Soatlik narx</b> — 1 soatlik ijara narxi (kunduzgi / tungi);\n"
            "6️⃣ <b>Zaklad sharti</b> — bron uchun oldindan zaklad olinishi yoki olinmasligi.\n\n"
            "Ariza topshirish uchun <b>«🏟 Stadion joylash (Ariza qoldirish)»</b> tugmasini bosing."
        )
    elif faq_type == "duration":
        answer = (
            "⏳ <b>Ariza qancha vaqtda tasdiqlanadi?</b>\n\n"
            "Yuborilgan har bir stadion arizasi adminlarimiz tomonidan o'rganib chiqiladi.\n"
            "Odatda ko'rib chiqish vaqti <b>15 daqiqadan 2 soatgacha</b> davom etadi.\n\n"
            "Ariza holati o'zgarganda sizga bot orqali avtomatik bildirishnoma keladi."
        )
    elif faq_type == "deposit":
        answer = (
            "💰 <b>Zaklad va to'lov tartibi:</b>\n\n"
            "Stadioningizda oldindan zaklad (avans) olish qoidasi bormi yoki yo'qligini "
            "ariza to'ldirish vaqtida ko'rsatishingiz zarur.\n"
            "Bu mijozlar bilan tushunmovchiliklar bo'lmasligi va bron qilish shaffof bo'lishi uchun xizmat qiladi."
        )
    elif faq_type == "feedback":
        answer = (
            "📝 <b>Taklif yoki shikoyat yuborish tartibi:</b>\n\n"
            "Botimiz xizmatini yaxshilash yoki stadionlar bo'yicha e'tirozingiz bo'lsa, "
            "<b>«📝 Taklif va shikoyat yuborish»</b> bo'limidan foydalanishingiz mumkin.\n\n"
            "Murojaatingiz to'g'ridan-to'g'ri adminlarga boradi va adminlar javob yozganda bot sizga yetkazadi."
        )
    else:
        answer = "Batafsil ma'lumot uchun adminlarimizga murojaat qiling."

    await callback.answer()
    await callback.message.answer(answer, parse_mode="HTML")


@router.message(F.text)
async def auto_reply_keywords(message: Message, state: FSMContext):
    """
    FSM dan tashqarida foydalanuvchi erkin matn yozganda kalit so'zlar bo'yicha
    avtomatik yo'naltiruvchi javob qaytarish.
    """
    current_state = await state.get_state()
    # Agar foydalanuvchi biror FSM jarayonida bo'lsa, bu handler aralashmaydi
    if current_state is not None:
        return

    text_lower = message.text.lower()

    # Stadion joylash bo'yicha so'rovlar
    stadium_keywords = ["stadion", "joylash", "qo'shish", "qoshish", "parametr", "narx", "qanday qo'shaman", "qanday qoshiladi", "maydon"]
    if any(k in text_lower for k in stadium_keywords):
        await message.answer(
            "🏟 <b>Stadion joylash haqida ma'lumot:</b>\n\n"
            "Stadioningizni botga kiritish uchun 6 ta aniq parametr (viloyat, manzil, telefon, kamida 2 ta rasm, soatlik narx va zaklad) talab etiladi.\n\n"
            "Arizani boshlash uchun quyidagi <b>«🏟 Stadion joylash (Ariza qoldirish)»</b> tugmasini bosing!",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
        return

    # Taklif, shikoyat, muammo bo'yicha so'rovlar
    feedback_keywords = ["shikoyat", "taklif", "muammo", "yordam", "bog'lanish", "aloqa", "kontakt"]
    if any(k in text_lower for k in feedback_keywords):
        await message.answer(
            "📝 <b>Taklif, shikoyat yoki savolingiz bormi?</b>\n\n"
            "Siz o'z murojaatingizni to'g'ridan-to'g'ri adminlarimizga yo'llashingiz mumkin.\n"
            "Buning uchun quyidagi <b>«📝 Taklif va shikoyat yuborish»</b> tugmasini bosing!",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
        return

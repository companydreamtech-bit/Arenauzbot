import re
from typing import List
from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InputMediaPhoto
)
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, GROUP_IDS
from database import add_stadium, get_user_stadiums
from states.stadium_state import StadiumForm
from keyboards.user_kb import (
    main_menu_keyboard,
    cancel_keyboard,
    phone_keyboard,
    photos_keyboard,
    regions_keyboard,
    deposit_keyboard,
    preview_keyboard
)
from keyboards.admin_kb import stadium_moderation_keyboard

router = Router()


def normalize_phone(phone_str: str) -> str | None:
    """Telefon raqamini tekshirish va yagona formatga keltirish"""
    digits = re.sub(r"\D", "", phone_str)
    if digits.startswith("998") and len(digits) == 12:
        return f"+{digits}"
    elif len(digits) == 9:
        return f"+998{digits}"
    return None


# ===================== ARIZANI BOSHLASH =====================

@router.message(F.text.in_(["🏟 Stadion joylashtirish", "🏟 Stadion joylash", "🏟 Stadion joylash (Ariza qoldirish)"]))
async def start_stadium_registration(message: Message, state: FSMContext):
    """Stadion joylash jarayonini boshlash"""
    await state.clear()
    await state.update_data(photos=[])
    await state.set_state(StadiumForm.region)

    text = (
        "🏟 <b>Stadion joylash bo'yicha ariza qoldirish</b>\n\n"
        "<b>1-qadam:</b> Stadioningiz qaysi viloyat/hududda joylashgan?\n"
        "Quyidagi ro'yxatdan tegishli hududni tanlang:"
    )
    # Avval bekor qilish tugmasi chiqishi uchun pastki klaviaturani yangilaymiz
    await message.answer("Jarayonni xohlagan vaqtda «❌ Bekor qilish» tugmasi orqali to'xtatishingiz mumkin.", reply_markup=cancel_keyboard())
    await message.answer(text, reply_markup=regions_keyboard(), parse_mode="HTML")


# ===================== 1-QADAM: VILOYAT =====================

@router.callback_query(StadiumForm.region, F.data.startswith("region:"))
async def process_region(callback: CallbackQuery, state: FSMContext):
    region_name = callback.data.split(":", 1)[1]
    await state.update_data(region=region_name)
    await state.set_state(StadiumForm.address)

    await callback.message.edit_text(
        f"✅ Tanlangan hudud: <b>{region_name}</b>",
        parse_mode="HTML"
    )

    prompt = (
        "🗺 <b>2-qadam: Manzil</b>\n\n"
        "Stadion nomi, to'liq manzili va mo'ljalini yozib yuboring.\n"
        "<i>(Masalan: Bunyodkor stadioni, Chilonzor tumani, Muqimiy ko'chasi 45-uy, metro bekati yaqinida)</i>"
    )
    await callback.message.answer(prompt, reply_markup=cancel_keyboard(), parse_mode="HTML")
    await callback.answer()


# ===================== 2-QADAM: MANZIL =====================

@router.message(StadiumForm.address, F.text)
async def process_address(message: Message, state: FSMContext):
    address = message.text.strip()
    if len(address) < 5:
        await message.answer(
            "⚠️ Manzil juda qisqa. Iltimos, stadion nomi va manzilini batafsilroq yozing (kamida 5 ta belgi):",
            reply_markup=cancel_keyboard()
        )
        return

    await state.update_data(address=address)
    await state.set_state(StadiumForm.phone)

    text = (
        "📞 <b>3-qadam: Telefon raqami</b>\n\n"
        "Mijozlar va adminlar bog'lanishi uchun mas'ul shaxsning telefon raqamini yuboring.\n\n"
        "Pastdagi <b>«📱 Telefon raqamni yuborish»</b> tugmasini bosing yoki qo'lda kiriting "
        "<i>(Masalan: +998901234567)</i>:"
    )
    await message.answer(text, reply_markup=phone_keyboard(), parse_mode="HTML")


# ===================== 3-QADAM: TELEFON =====================

@router.message(StadiumForm.phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"

    await state.update_data(phone=phone)
    await state.set_state(StadiumForm.photos)

    text = (
        f"✅ Telefon raqamingiz qabul qilindi: <b>{phone}</b>\n\n"
        "📸 <b>4-qadam: Stadion rasmlari (KAMIDA 2 TA)</b>\n\n"
        "Stadionning kamida 2 ta sifatli rasmini yuboring (maydon qoplamasi, yoritish chiroqlari, kiyim almashtirish xonasi va h.k.).\n\n"
        "Rasmlarni ketma-ket bittalab yoki bir vaqtda albom qilib yuborishingiz mumkin (maksimal 10 tagacha)."
    )
    await message.answer(text, reply_markup=photos_keyboard(0), parse_mode="HTML")


@router.message(StadiumForm.phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    clean_phone = normalize_phone(message.text)
    if not clean_phone:
        await message.answer(
            "⚠️ Noto'g'ri telefon raqami formati!\n"
            "Iltimos, pastdagi «📱 Telefon raqamni yuborish» tugmasidan foydalaning "
            "yoki raqamni <code>+998901234567</code> formatida yozing:",
            reply_markup=phone_keyboard(),
            parse_mode="HTML"
        )
        return

    await state.update_data(phone=clean_phone)
    await state.set_state(StadiumForm.photos)

    text = (
        f"✅ Telefon raqamingiz qabul qilindi: <b>{clean_phone}</b>\n\n"
        "📸 <b>4-qadam: Stadion rasmlari (KAMIDA 2 TA)</b>\n\n"
        "Stadionning kamida 2 ta sifatli rasmini yuboring (maydon, kiyinish xonasi va h.k.).\n\n"
        "Rasmlarni ketma-ket yoki bitta albom qilib yuborishingiz mumkin (maksimal 10 ta)."
    )
    await message.answer(text, reply_markup=photos_keyboard(0), parse_mode="HTML")


# ===================== 4-QADAM: RASMLAR =====================

@router.message(StadiumForm.photos, F.photo)
async def process_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos: List[str] = data.get("photos", [])

    if len(photos) >= 10:
        await message.answer(
            f"⚠️ Siz allaqachon maksimal 10 ta rasm yukladingiz.\n"
            "Keyingi bosqichga o'tish uchun «✅ Rasmlarni yakunlash ({len(photos)} ta)» tugmasini bosing.",
            reply_markup=photos_keyboard(len(photos))
        )
        return

    file_id = message.photo[-1].file_id
    photos.append(file_id)
    await state.update_data(photos=photos)
    count = len(photos)

    if count == 1:
        await message.answer(
            "📸 1-rasm qabul qilindi.\n"
            "⚠️ <b>Talab:</b> Stadion bo'yicha kamida 2 ta rasm bo'lishi shart. Yana kamida 1 ta rasm yuboring:",
            reply_markup=photos_keyboard(count),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"📸 <b>{count}-rasm muvaffaqiyatli qabul qilindi.</b>\n\n"
            "Yana rasm yuborishingiz yoki yetarli bo'lsa, quyidagi "
            f"<b>«✅ Rasmlarni yakunlash ({count} ta)»</b> tugmasini bosib keyingi bosqichga o'tishingiz mumkin.",
            reply_markup=photos_keyboard(count),
            parse_mode="HTML"
        )


@router.message(StadiumForm.photos, F.text.startswith("✅ Rasmlarni yakunlash"))
async def finish_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos: List[str] = data.get("photos", [])

    if len(photos) < 2:
        await message.answer(
            "⚠️ Stadion rasmlari kamida 2 ta bo'lishi shart!\n"
            f"Hozirda yuklangan rasmlar: {len(photos)} ta. Yana rasm yuboring:",
            reply_markup=photos_keyboard(len(photos))
        )
        return

    await state.set_state(StadiumForm.hourly_price)
    text = (
        "💰 <b>5-qadam: Soatlik narxi</b>\n\n"
        "Stadionning 1 soatlik ijara narxini yozing.\n"
        "<i>(Masalan: 120 000 so'm yoki Kunduzi 100 ming, kechasi 150 ming so'm)</i>:"
    )
    await message.answer(text, reply_markup=cancel_keyboard(), parse_mode="HTML")


# ===================== 5-QADAM: NARXI =====================

@router.message(StadiumForm.hourly_price, F.text)
async def process_hourly_price(message: Message, state: FSMContext):
    price = message.text.strip()
    if len(price) < 2:
        await message.answer("⚠️ Iltimos, narxni to'g'ri kiriting:", reply_markup=cancel_keyboard())
        return

    await state.update_data(hourly_price=price)
    await state.set_state(StadiumForm.takes_deposit)

    text = (
        "🤝 <b>6-qadam: Zaklad (avans) sharti</b>\n\n"
        "Mijozlar stadionni bron qilganda oldindan zaklad (avans) olinadimi?"
    )
    await message.answer(text, reply_markup=deposit_keyboard(), parse_mode="HTML")


# ===================== 6-QADAM: ZAKLAD VA PREVIEW =====================

@router.callback_query(StadiumForm.takes_deposit, F.data.startswith("deposit:"))
async def process_deposit(callback: CallbackQuery, state: FSMContext):
    deposit_choice = callback.data.split(":")[1]
    takes_deposit_str = "Ha, zaklad olinadi" if deposit_choice == "ha" else "Yo'q, zaklad olinmaydi"
    
    await state.update_data(takes_deposit=takes_deposit_str)
    await state.set_state(StadiumForm.confirm)

    data = await state.get_data()
    photos: List[str] = data.get("photos", [])

    await callback.message.edit_text(f"🤝 Zaklad sharti: <b>{takes_deposit_str}</b>", parse_mode="HTML")

    # Rasmlar albomini foydalanuvchiga ko'rsatamiz
    if photos:
        media_group = [InputMediaPhoto(media=pid) for pid in photos[:10]]
        await callback.message.answer_media_group(media=media_group)

    # Parametrlar kartochkasi
    card_text = (
        "🏟 <b>STADION ARIZASI (TEKSHIRISH)</b>\n\n"
        f"📍 <b>Viloyat:</b> {data.get('region')}\n"
        f"🗺 <b>Manzil:</b> {data.get('address')}\n"
        f"📞 <b>Telefon raqam:</b> {data.get('phone')}\n"
        f"📸 <b>Rasmlar soni:</b> {len(photos)} ta\n"
        f"💰 <b>Soatlik narxi:</b> {data.get('hourly_price')}\n"
        f"🤝 <b>Zaklad oladimi:</b> {takes_deposit_str}\n\n"
        "<i>Ma'lumotlar to'g'ri bo'lsa, «📤 Arizani tasdiqlash va yuborish» tugmasini bosing:</i>"
    )
    await callback.message.answer(card_text, reply_markup=preview_keyboard(), parse_mode="HTML")
    await callback.answer()


# ===================== YAKUNIY TASDIQLASH =====================

@router.callback_query(StadiumForm.confirm, F.data == "confirm_stadium:yes")
async def confirm_and_submit_stadium(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user = callback.from_user
    photos: List[str] = data.get("photos", [])

    stadium_id = add_stadium(
        user_id=user.id,
        username=user.username,
        region=data.get("region", ""),
        address=data.get("address", ""),
        phone=data.get("phone", ""),
        photos=photos,
        hourly_price=data.get("hourly_price", ""),
        takes_deposit=data.get("takes_deposit", "")
    )

    await state.clear()

    # Foydalanuvchiga xabar
    user_msg = (
        f"🎉 <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"Ariza raqami: <b>#{stadium_id}</b>\n"
        f"Holati: ⏳ <i>Ko'rib chiqilmoqda</i>\n\n"
        "Adminlarimiz arizangizni tekshirib chiqqach, sizga ushbu bot orqali tasdiq xabari yuboriladi."
    )
    await callback.message.answer(user_msg, reply_markup=main_menu_keyboard(is_admin=user.id in ADMIN_IDS), parse_mode="HTML")
    await callback.answer("Arizangiz qabul qilindi!")

    # Barcha adminlarga bildirishnoma yuborish
    admin_card = (
        f"🆕 <b>YANGI STADION ARIZASI #{stadium_id}</b>\n\n"
        f"👤 <b>Yuboruvchi:</b> @{user.username or 'username_yoq'} (ID: <code>{user.id}</code>)\n"
        f"📍 <b>Viloyat:</b> {data.get('region')}\n"
        f"🗺 <b>Manzil:</b> {data.get('address')}\n"
        f"📞 <b>Telefon:</b> {data.get('phone')}\n"
        f"💰 <b>Soatlik narx:</b> {data.get('hourly_price')}\n"
        f"🤝 <b>Zaklad:</b> {data.get('takes_deposit')}\n"
        f"📸 <b>Rasmlar soni:</b> {len(photos)} ta\n"
        f"⏳ <b>Holat:</b> Ko'rib chiqilmoqda"
    )

    target_chats = list(dict.fromkeys(ADMIN_IDS + GROUP_IDS))
    for chat_id in target_chats:
        try:
            if photos:
                media_group = [InputMediaPhoto(media=pid) for pid in photos[:10]]
                await bot.send_media_group(chat_id=chat_id, media=media_group)
            await bot.send_message(
                chat_id=chat_id,
                text=admin_card,
                reply_markup=stadium_moderation_keyboard(stadium_id),
                parse_mode="HTML"
            )
        except Exception:
            pass


@router.callback_query(StadiumForm.confirm, F.data == "confirm_stadium:restart")
async def restart_stadium_form(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.update_data(photos=[])
    await state.set_state(StadiumForm.region)

    await callback.message.answer(
        "🔄 <b>Ariza qaytadan to'ldirishga o'tkazildi.</b>\n\n"
        "<b>1-qadam:</b> Qaysi viloyat/hududdansiz?",
        reply_markup=regions_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(StadiumForm.confirm, F.data == "confirm_stadium:cancel")
async def cancel_stadium_form(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "❌ <b>Ariza to'ldirish bekor qilindi.</b>",
        reply_markup=main_menu_keyboard(is_admin=callback.from_user.id in ADMIN_IDS),
        parse_mode="HTML"
    )
    await callback.answer("Bekor qilindi")


# ===================== MENING ARIZALARIM =====================

@router.message(F.text == "📋 Mening arizalarim")
async def show_my_applications(message: Message):
    user_id = message.from_user.id
    stadiums = get_user_stadiums(user_id)

    if not stadiums:
        await message.answer(
            "📋 <b>Sizda hali yuborilgan stadion arizalari mavjud emas.</b>\n\n"
            "Stadioningizni qo'shish uchun «🏟 Stadion joylash (Ariza qoldirish)» tugmasini bosing.",
            reply_markup=main_menu_keyboard(is_admin=user_id in ADMIN_IDS),
            parse_mode="HTML"
        )
        return

    text = f"📋 <b>Sizning stadion arizalaringiz (jami {len(stadiums)} ta):</b>\n\n"
    
    status_emojis = {
        "pending": "⏳ Ko'rib chiqilmoqda",
        "approved": "✅ Tasdiqlangan",
        "rejected": "❌ Rad etilgan"
    }

    for idx, s in enumerate(stadiums, start=1):
        status_text = status_emojis.get(s["status"], s["status"])
        created = str(s.get("created_at", ""))[:19]
        text += (
            f"<b>{idx}. Ariza #{s['id']}</b>\n"
            f"📍 Viloyat: {s['region']}\n"
            f"🗺 Manzil: {s['address']}\n"
            f"📞 Telefon: {s['phone']}\n"
            f"💰 Narxi: {s['hourly_price']}\n"
            f"🤝 Zaklad: {s['takes_deposit']}\n"
            f"Holati: <b>{status_text}</b>\n"
            f"Sana: <i>{created}</i>\n"
            f"---------------------------------\n"
        )

    await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from database import (
    get_stadium,
    update_stadium_status,
    get_stadiums_by_status,
    count_stadiums,
    get_feedback,
    update_feedback_reply,
    get_feedbacks_by_status,
    count_feedbacks
)
from states.admin_state import AdminReplyState
from aiogram.fsm.storage.base import StorageKey
from config import ADMIN_IDS, GROUP_IDS

router = Router()


def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish"""
    return user_id in ADMIN_IDS


async def has_admin_permission(bot: Bot, chat_id: int, user_id: int) -> bool:
    """Foydalanuvchining admin huquqini tekshirish (shaxsiy yoki guruh admini)"""
    if user_id in ADMIN_IDS:
        return True
    if chat_id < 0:
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            if member.status in ["creator", "administrator"]:
                return True
        except Exception:
            pass
    return False


# ===================== ADMIN PANEL BOSHQARUVI =====================

@router.message(Command("admin"), StateFilter("*"))
@router.message(F.text.in_(["👑 Admin paneli", "Admin paneli", "Admin", "👑 Admin"]), StateFilter("*"))
async def cmd_admin(message: Message, state: FSMContext):
    """Admin panel asosiy sahifasi"""
    await state.clear()
    if not is_admin(message.from_user.id):
        await message.answer(
            f"⛔️ Kechirasiz, ushbu bo'lim faqat bot administratorlari uchun mo'ljallangan.\n"
            f"Sizning Telegram ID raqamingiz: <code>{message.from_user.id}</code>",
            parse_mode="HTML"
        )
        return

    stadium_stats = count_stadiums()
    fb_stats = count_feedbacks()

    text = (
        "👑 <b>ArenaBot Admin Paneli</b>\n\n"
        "📊 <b>Stadion arizalari statistikasi:</b>\n"
        f"• Jami arizalar: <b>{stadium_stats['total']} ta</b>\n"
        f"• ⏳ Kutilayotgan: <b>{stadium_stats['pending']} ta</b>\n"
        f"• ✅ Tasdiqlangan: <b>{stadium_stats['approved']} ta</b>\n"
        f"• ❌ Rad etilgan: <b>{stadium_stats['rejected']} ta</b>\n\n"
        "📬 <b>Murojaatlar (Taklif/Shikoyat) statistikasi:</b>\n"
        f"• Jami murojaatlar: <b>{fb_stats['total']} ta</b>\n"
        f"• 🆕 Yangi (javob berilmagan): <b>{fb_stats['new']} ta</b>\n"
        f"• ✉️ Javob berilgan: <b>{fb_stats['answered']} ta</b>\n\n"
        "Quyidagi tugmalar orqali tegishli bo'limlarga o'ting:"
    )
    await message.answer(text, reply_markup=admin_panel_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "admin_view:stats")
async def callback_admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return

    stadium_stats = count_stadiums()
    fb_stats = count_feedbacks()

    text = (
        "👑 <b>ArenaBot Admin Paneli</b>\n\n"
        "📊 <b>Stadion arizalari statistikasi:</b>\n"
        f"• Jami arizalar: <b>{stadium_stats['total']} ta</b>\n"
        f"• ⏳ Kutilayotgan: <b>{stadium_stats['pending']} ta</b>\n"
        f"• ✅ Tasdiqlangan: <b>{stadium_stats['approved']} ta</b>\n"
        f"• ❌ Rad etilgan: <b>{stadium_stats['rejected']} ta</b>\n\n"
        "📬 <b>Murojaatlar (Taklif/Shikoyat) statistikasi:</b>\n"
        f"• Jami murojaatlar: <b>{fb_stats['total']} ta</b>\n"
        f"• 🆕 Yangi: <b>{fb_stats['new']} ta</b>\n"
        f"• ✉️ Javob berilgan: <b>{fb_stats['answered']} ta</b>"
    )
    await callback.message.edit_text(text, reply_markup=admin_panel_keyboard(), parse_mode="HTML")
    await callback.answer("Statistika yangilandi")


@router.callback_query(F.data == "admin_view:pending_stadiums")
async def callback_pending_stadiums(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return

    pending = get_stadiums_by_status("pending", limit=10)
    if not pending:
        await callback.answer("Hozirda kutilayotgan arizalar yo'q!", show_alert=True)
        return

    await callback.answer()
    for s in pending:
        photos = s.get("photos", [])
        card = (
            f"🏟 <b>Kutilayotgan ariza #{s['id']}</b>\n\n"
            f"👤 Foydalanuvchi: @{s.get('username') or 'yoq'} (ID: <code>{s['user_id']}</code>)\n"
            f"📍 Viloyat: {s['region']}\n"
            f"🗺 Manzil: {s['address']}\n"
            f"📞 Telefon: {s['phone']}\n"
            f"💰 Soatlik narxi: {s['hourly_price']}\n"
            f"🤝 Zaklad: {s['takes_deposit']}\n"
            f"Sana: <i>{str(s.get('created_at', ''))[:19]}</i>"
        )
        if photos:
            try:
                media_group = [InputMediaPhoto(media=pid) for pid in photos[:10]]
                await bot.send_media_group(chat_id=callback.from_user.id, media=media_group)
            except Exception:
                pass
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=card,
            reply_markup=stadium_moderation_keyboard(s["id"]),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "admin_view:new_feedbacks")
async def callback_new_feedbacks(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return

    new_fbs = get_feedbacks_by_status("new", limit=10)
    if not new_fbs:
        await callback.answer("Yangi murojaatlar mavjud emas!", show_alert=True)
        return

    await callback.answer()
    for fb in new_fbs:
        text = (
            f"📩 <b>Murojaat #{fb['id']}</b>\n\n"
            f"📌 Turi: <b>{fb['feedback_type']}</b>\n"
            f"👤 Yuboruvchi: @{fb.get('username') or 'yoq'} (ID: <code>{fb['user_id']}</code>)\n"
            f"📞 Telefon: {fb.get('phone', 'Koʻrsatilmagan')}\n"
            f"Sana: <i>{str(fb.get('created_at', ''))[:19]}</i>\n\n"
            f"💬 <b>Matn:</b>\n{fb['text']}"
        )
        if fb.get("photo_id"):
            try:
                await bot.send_photo(
                    chat_id=callback.from_user.id,
                    photo=fb["photo_id"],
                    caption=text,
                    reply_markup=feedback_reply_keyboard(fb["id"]),
                    parse_mode="HTML"
                )
                continue
            except Exception:
                pass

        await bot.send_message(
            chat_id=callback.from_user.id,
            text=text,
            reply_markup=feedback_reply_keyboard(fb["id"]),
            parse_mode="HTML"
        )


# ===================== STADION MODERATSIYASI =====================

@router.callback_query(F.data.startswith("approve:"))
async def approve_stadium(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    if not await has_admin_permission(bot, chat_id, user_id):
        await callback.answer("Sizda ushbu amalni bajarish uchun ruxsat yo'q!", show_alert=True)
        return

    stadium_id = int(callback.data.split(":")[1])
    stadium = get_stadium(stadium_id)

    if not stadium:
        await callback.answer("Ariza topilmadi!", show_alert=True)
        return

    update_stadium_status(stadium_id, "approved")
    admin_name = callback.from_user.full_name or callback.from_user.username or "Admin"

    # Admin yoki guruh xabaridagi tugmalarni o'chirib, holatni yangilaymiz
    new_text = f"{callback.message.text or callback.message.caption or ''}\n\n✅ <b>TASDIQLANDI</b> (Admin: {admin_name})"
    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=new_text, reply_markup=None, parse_mode="HTML")
        else:
            await callback.message.edit_text(text=new_text, reply_markup=None, parse_mode="HTML")
    except Exception:
        pass

    await callback.answer(f"Ariza #{stadium_id} tasdiqlandi!")

    # Foydalanuvchiga bildirishnoma yuborish
    try:
        user_notify = (
            f"🎉 <b>Ajoyib yangilik!</b>\n\n"
            f"Sizning <b>#{stadium_id}</b>-sonli stadion joylash bo'yicha arizangiz "
            f"adminlarimiz tomonidan <b>TASDIQLANDI</b>! ✅\n\n"
            f"Manzil: {stadium['address']}\n"
            f"Viloyat: {stadium['region']}"
        )
        await bot.send_message(chat_id=stadium["user_id"], text=user_notify, parse_mode="HTML")
    except Exception:
        pass


@router.callback_query(F.data.startswith("reject:"))
async def reject_stadium(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    if not await has_admin_permission(bot, chat_id, user_id):
        await callback.answer("Sizda ushbu amalni bajarish uchun ruxsat yo'q!", show_alert=True)
        return

    stadium_id = int(callback.data.split(":")[1])
    stadium = get_stadium(stadium_id)

    if not stadium:
        await callback.answer("Ariza topilmadi!", show_alert=True)
        return

    update_stadium_status(stadium_id, "rejected")
    admin_name = callback.from_user.full_name or callback.from_user.username or "Admin"

    new_text = f"{callback.message.text or callback.message.caption or ''}\n\n❌ <b>RAD ETILDI</b> (Admin: {admin_name})"
    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=new_text, reply_markup=None, parse_mode="HTML")
        else:
            await callback.message.edit_text(text=new_text, reply_markup=None, parse_mode="HTML")
    except Exception:
        pass

    await callback.answer(f"Ariza #{stadium_id} rad etildi!")

    # Foydalanuvchiga bildirishnoma yuborish
    try:
        user_notify = (
            f"❌ <b>Arizangiz rad etildi</b>\n\n"
            f"Sizning <b>#{stadium_id}</b>-sonli stadion arizangiz tekshiruvdan o'tmadi va rad etildi.\n"
            f"Iltimos, ma'lumotlar va rasmlarni to'g'rilab, qaytadan ariza qoldiring."
        )
        await bot.send_message(chat_id=stadium["user_id"], text=user_notify, parse_mode="HTML")
    except Exception:
        pass


# ===================== MUROJAATGA JAVOB YOZISH =====================

@router.callback_query(F.data.startswith("reply_fb:"))
async def start_reply_feedback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    if not await has_admin_permission(bot, chat_id, user_id):
        await callback.answer("Sizda javob yozish uchun ruxsat yo'q!", show_alert=True)
        return

    feedback_id = int(callback.data.split(":")[1])
    fb = get_feedback(feedback_id)
    if not fb:
        await callback.answer("Murojaat topilmadi!", show_alert=True)
        return

    # Agar guruhda bosilgan bo'lsa
    if callback.message.chat.type in ["group", "supergroup"]:
        try:
            user_state = FSMContext(
                storage=state.storage,
                key=StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
            )
            await user_state.update_data(reply_feedback_id=feedback_id)
            await user_state.set_state(AdminReplyState.reply_text)

            prompt_text = (
                f"✍️ <b>#{feedback_id}-sonli murojaatga javob yozing:</b>\n\n"
                f"📌 <b>Turi:</b> {fb['feedback_type']}\n"
                f"👤 <b>Foydalanuvchi:</b> @{fb.get('username') or 'yoq'} (ID: <code>{fb['user_id']}</code>)\n"
                f"💬 <b>Matn:</b> <i>«{fb['text'][:300]}»</i>\n\n"
                "Javobingizni shu yerga yozing. Bekor qilish uchun <code>❌ Bekor qilish</code> deb yozing."
            )
            await bot.send_message(chat_id=user_id, text=prompt_text, parse_mode="HTML")
            await callback.answer("📩 Bot sizga shaxsiy xabarda javob yozish formasini ochdi!", show_alert=True)
        except Exception:
            bot_info = await bot.get_me()
            await callback.answer(
                f"⚠️ Bot shaxsiy chatiga kirib /start bosing: @{bot_info.username}",
                show_alert=True
            )
        return

    # Shaxsiy chatda bo'lsa
    await state.update_data(reply_feedback_id=feedback_id)
    await state.set_state(AdminReplyState.reply_text)

    await callback.message.answer(
        f"✍️ <b>#{feedback_id}-sonli murojaatga javob yozing:</b>\n\n"
        f"Murojaat matni: <i>«{fb['text'][:200]}...»</i>\n\n"
        "Javobingiz to'g'ridan-to'g'ri foydalanuvchiga yetkaziladi.\n"
        "Bekor qilish uchun <code>/cancel</code> yoki <code>❌ Bekor qilish</code> deb yozing.",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminReplyState.reply_text, F.text)
async def process_admin_reply_text(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return

    reply_content = message.text.strip()
    data = await state.get_data()
    feedback_id = data.get("reply_feedback_id")

    if not feedback_id:
        await state.clear()
        await message.answer("Xatolik: Murojaat ID si topilmadi.")
        return

    fb = get_feedback(feedback_id)
    if not fb:
        await state.clear()
        await message.answer("Xatolik: Murojaat bazadan topilmadi.")
        return

    # Bazada yangilash
    update_feedback_reply(feedback_id, reply_content)
    await state.clear()

    # Foydalanuvchiga yetkazish
    try:
        user_message = (
            f"📩 <b>Sizning #{feedback_id}-sonli murojaatingizga admin javobi:</b>\n\n"
            f"«{reply_content}»\n\n"
            f"<i>Murojaatingiz uchun tashakkur!</i>"
        )
        await bot.send_message(chat_id=fb["user_id"], text=user_message, parse_mode="HTML")
        await message.answer(f"✅ Javobingiz #{feedback_id}-sonli murojaat egasiga muvaffaqiyatli yuborildi!")
    except Exception as e:
        await message.answer(f"⚠️ Foydalanuvchiga xabar yuborishda xatolik yuz berdi (foydalanuvchi botni bloklagan bo'lishi mumkin): {e}")

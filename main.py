import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_IDS, GROUP_IDS
from database import init_db
from handlers import common, stadium, feedback, admin

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ArenaBot")


async def main() -> None:
    # 1. Ma'lumotlar bazasini initsializatsiya qilish
    init_db()
    logger.info("SQLite ma'lumotlar bazasi va jadvallar muvaffaqiyatli tekshirildi.")

    # 2. Token tekshiruvi
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "\n[XATOLIK] BOT_TOKEN topilmadi yoki noto'g'ri ko'rsatilgan!\n"
            "Iltimos, loyiha ildizidagi '.env' faylini ochib, BotFather dan olingan bot tokeningizni kiriting.\n"
            "Misol: BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ\n"
        )
        sys.exit(1)

    # 3. Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # 4. Routerlarni tartib bo'yicha ulash
    # Muhim: admin va maxsus formalar oldin, umumiy handlerlar oxirida ulanishi kerak
    dp.include_router(admin.router)
    dp.include_router(stadium.router)
    dp.include_router(feedback.router)
    dp.include_router(common.router)

    # 5. Adminlar va guruhlarga start bildirishnomasi
    notify_chats = list(dict.fromkeys(ADMIN_IDS + GROUP_IDS))
    for chat_id in notify_chats:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="🚀 <b>ArenaBot muvaffaqiyatli ishga tushdi!</b>\nBoshqaruv uchun <code>/admin</code> buyrug'idan foydalaning."
            )
        except Exception:
            pass

    logger.info("Bot polling rejimida ishga tushmoqda...")
    # Eskirgan yangilanishlarni tashlab yuborish
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")

import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

def parse_ids(raw_str: str) -> list[int]:
    """Vergul bilan ajratilgan ID larni (musbat va manfiy guruh ID larini) tahlil qilish"""
    result: list[int] = []
    if not raw_str:
        return result
    for item in raw_str.split(","):
        clean = item.strip().strip("'\"")
        if (clean.startswith("-") and clean[1:].isdigit()) or clean.isdigit():
            result.append(int(clean))
    return result

# Admin Telegram ID lari (shaxsiy profillar)
ADMIN_IDS: list[int] = parse_ids(os.getenv("ADMIN_IDS", ""))

# Telegram guruh yoki kanal ID lari (masalan: -1001234567890)
GROUP_IDS: list[int] = parse_ids(os.getenv("GROUP_ID", "") or os.getenv("GROUP_IDS", ""))

DB_PATH: str = os.getenv("DB_PATH", str(BASE_DIR / "stadion_bot.db"))


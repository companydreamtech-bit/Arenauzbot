import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Ma'lumotlar bazasi va jadvallarni yaratish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. stadiums jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stadiums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                region TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                photos_json TEXT NOT NULL,
                hourly_price TEXT NOT NULL,
                takes_deposit TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. feedbacks jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                feedback_type TEXT NOT NULL,
                phone TEXT,
                text TEXT NOT NULL,
                photo_id TEXT,
                admin_reply TEXT,
                status TEXT NOT NULL DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


# ===================== STADIUM CRUD =====================

def add_stadium(
    user_id: int,
    username: Optional[str],
    region: str,
    address: str,
    phone: str,
    photos: List[str],
    hourly_price: str,
    takes_deposit: str
) -> int:
    """Yangi stadion arizasini bazaga qo'shish va ID sini qaytarish"""
    photos_json = json.dumps(photos, ensure_ascii=False)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO stadiums (user_id, username, region, address, phone, photos_json, hourly_price, takes_deposit, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (user_id, username, region, address, phone, photos_json, hourly_price, takes_deposit))
        conn.commit()
        return cursor.lastrowid


def get_stadium(stadium_id: int) -> Optional[Dict[str, Any]]:
    """ID bo'yicha stadion ma'lumotlarini olish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stadiums WHERE id = ?", (stadium_id,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            try:
                data["photos"] = json.loads(data["photos_json"])
            except Exception:
                data["photos"] = []
            return data
        return None


def get_user_stadiums(user_id: int) -> List[Dict[str, Any]]:
    """Foydalanuvchining barcha arizalarini olish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM stadiums 
            WHERE user_id = ? 
            ORDER BY id DESC
        """, (user_id,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            try:
                d["photos"] = json.loads(d["photos_json"])
            except Exception:
                d["photos"] = []
            result.append(d)
        return result


def update_stadium_status(stadium_id: int, status: str) -> bool:
    """Stadion arizasi holatini yangilash ('approved', 'rejected')"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE stadiums 
            SET status = ? 
            WHERE id = ?
        """, (status, stadium_id))
        conn.commit()
        return cursor.rowcount > 0


def get_stadiums_by_status(status: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Status bo'yicha stadionlar ro'yxatini olish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM stadiums 
            WHERE status = ? 
            ORDER BY id DESC 
            LIMIT ?
        """, (status, limit))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            try:
                d["photos"] = json.loads(d["photos_json"])
            except Exception:
                d["photos"] = []
            result.append(d)
        return result


def count_stadiums() -> Dict[str, int]:
    """Stadionlar statistikasi"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM stadiums")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM stadiums WHERE status = 'pending'")
        pending = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM stadiums WHERE status = 'approved'")
        approved = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM stadiums WHERE status = 'rejected'")
        rejected = cursor.fetchone()[0]

        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected
        }


# ===================== FEEDBACK CRUD =====================

def add_feedback(
    user_id: int,
    username: Optional[str],
    feedback_type: str,
    phone: Optional[str],
    text: str,
    photo_id: Optional[str] = None
) -> int:
    """Yangi taklif yoki shikoyatni saqlash"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedbacks (user_id, username, feedback_type, phone, text, photo_id, status)
            VALUES (?, ?, ?, ?, ?, ?, 'new')
        """, (user_id, username, feedback_type, phone, text, photo_id))
        conn.commit()
        return cursor.lastrowid


def get_feedback(feedback_id: int) -> Optional[Dict[str, Any]]:
    """ID bo'yicha murojaat ma'lumotlarini olish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedbacks WHERE id = ?", (feedback_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def update_feedback_reply(feedback_id: int, admin_reply: str) -> bool:
    """Admin javobini saqlash va statusni 'answered' qilish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE feedbacks 
            SET admin_reply = ?, status = 'answered' 
            WHERE id = ?
        """, (admin_reply, feedback_id))
        conn.commit()
        return cursor.rowcount > 0


def get_feedbacks_by_status(status: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Status bo'yicha taklif/shikoyatlarni olish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM feedbacks 
            WHERE status = ? 
            ORDER BY id DESC 
            LIMIT ?
        """, (status, limit))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def count_feedbacks() -> Dict[str, int]:
    """Murojaatlar statistikasi"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM feedbacks")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM feedbacks WHERE status = 'new'")
        new_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM feedbacks WHERE status = 'answered'")
        answered = cursor.fetchone()[0]

        return {
            "total": total,
            "new": new_count,
            "answered": answered
        }

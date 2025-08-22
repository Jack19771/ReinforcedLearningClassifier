# core/database.py
import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="data/classifier.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Tworzy tabele jeśli nie istnieją"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    text TEXT NOT NULL,
                    area TEXT NOT NULL,
                    subarea TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

    def save_document(self, text, area, subarea=None):
        """Zapisuje dokument do bazy"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO documents (text, area, subarea) VALUES (?, ?, ?)",
                (text, area, subarea)
            )
        return True
    def get_all_documents(self):
        """Pobiera wszystkie dokumenty z bazy"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, text, area, subarea, created_at 
                FROM documents 
                ORDER BY created_at DESC
            """)
            return cursor.fetchall()

    def get_categories(self):
        """Pobiera wszystkie unikalne Area i SubArea"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT DISTINCT area, subarea 
                FROM documents 
                WHERE area IS NOT NULL
            """)
            return cursor.fetchall()
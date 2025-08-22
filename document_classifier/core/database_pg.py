# core/database_pg.py
import psycopg2
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        # Pobieranie z environment variables
        self.db_config = {
            'host': os.getenv('DB_HOST', 'postgres-master-service'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'document_classifier'),
            'user': os.getenv('DB_USER', 'app_user'),
            'password': os.getenv('DB_PASSWORD', 'app_password')
        }
        self._init_database()
    
    def _get_connection(self):
        """Tworzy połączenie z PostgreSQL"""
        return psycopg2.connect(**self.db_config)
    
    def _init_database(self):
        """Tworzy tabele jeśli nie istnieją"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id SERIAL PRIMARY KEY,
                        text TEXT NOT NULL,
                        area TEXT NOT NULL,
                        subarea TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)
                conn.commit()

    def save_document(self, text, area, subarea=None):
        """Zapisuje dokument do bazy"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO documents (text, area, subarea) VALUES (%s, %s, %s)",
                    (text, area, subarea)
                )
                conn.commit()
        return True

    def get_all_documents(self):
        """Pobiera wszystkie dokumenty z bazy"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, text, area, subarea, created_at 
                    FROM documents 
                    ORDER BY created_at DESC
                """)
                return cursor.fetchall()

    def get_categories(self):
        """Pobiera wszystkie unikalne Area i SubArea"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT area, subarea 
                    FROM documents 
                    WHERE area IS NOT NULL
                """)
                return cursor.fetchall()
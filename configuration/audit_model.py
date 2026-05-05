import sqlite3
import json
from datetime import datetime
from configuration.config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


class AuditModel:

    def log(self, action, table, record_id, old_data, new_data, utilisateur):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO audit_log (
                action, table_name, record_id,
                old_data, new_data,
                utilisateur, date_heure
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            action,
            table,
            record_id,
            json.dumps(old_data) if old_data else None,
            json.dumps(new_data) if new_data else None,
            utilisateur,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def get_all(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM audit_log
            ORDER BY date_heure DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return rows
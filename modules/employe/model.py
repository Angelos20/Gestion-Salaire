import sqlite3
from configuration.database import get_connection  # Assure-toi que get_connection() renvoie une connexion SQLite valide

class EmployeModel:
    def __init__(self):
        self.conn = get_connection()

    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employes ORDER BY id DESC")
        rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_by_id(self, emp_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employes WHERE id = ?", (emp_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def create(self, data):
        conn = get_connection()
        cursor = conn.cursor()

        emp_id = data.get("id")

        # 🔍 vérifier si ID existe déjà
        cursor.execute("SELECT id FROM employes WHERE id = ?", (emp_id,))
        exists = cursor.fetchone()

        if exists:
            return None  # ID déjà utilisé

        cursor.execute("""
            INSERT INTO employes (
                id, nom, prenom, email, telephone,
                poste, date_embauche, salaire_base, adresse, statut
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            emp_id,
            data.get('nom'),
            data.get('prenom'),
            data.get('email'),
            data.get('telephone'),
            data.get('poste'),
            data.get('date_embauche'),
            data.get('salaire_base'),
            data.get('adresse'),
            data.get('statut', 'actif')
        ))

        conn.commit()
        return emp_id

    def update(self, emp_id, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE employes
            SET nom=?, prenom=?, email=?, telephone=?, poste=?, date_embauche=?, salaire_base=?, adresse=?, statut=?
            WHERE id = ?
        """, (
            data['nom'], data['prenom'], data['email'], data.get('telephone', ''),
            data.get('poste', ''), data.get('date_embauche', ''), data.get('salaire_base', 0),
            data.get('adresse', ''), data.get('statut', 'actif'), emp_id
        ))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete(self, emp_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM employes WHERE id = ?", (emp_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def search(self, term):
        cursor = self.conn.cursor()
        term = f"%{term}%"
        cursor.execute("""
            SELECT * FROM employes
            WHERE nom LIKE ? OR prenom LIKE ? OR email LIKE ?
            ORDER BY id DESC
        """, (term, term, term))
        rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_statistiques(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employes")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM employes WHERE statut = 'actif'")
        actifs = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(salaire_base) FROM employes")
        total_salaire = cursor.fetchone()[0] or 0
        return {"total": total, "actifs": actifs, "total_salaire": total_salaire}

    def _row_to_dict(self, row):
        return {
            'id': row[0], 'nom': row[1], 'prenom': row[2], 'email': row[3],
            'telephone': row[4], 'poste': row[5], 'date_embauche': row[6],
            'salaire_base': row[7], 'adresse': row[8], 'statut': row[9]
        }

    def get_postes_uniques(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT poste
            FROM employes
            WHERE poste IS NOT NULL AND poste != ''
        """)

        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows]
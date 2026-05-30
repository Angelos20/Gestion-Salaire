import sqlite3

from configuration.database import get_connection


class EmployeModel:

    def __init__(self):

        self.conn = get_connection()

    # ==================================================
    # GET ALL
    # ==================================================

    def get_all(self):

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT *
            FROM employes
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        return [
            self._row_to_dict(row)
            for row in rows
        ]

    # ==================================================
    # GET BY ID
    # ==================================================

    def get_by_id(self, emp_id):

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT *
            FROM employes
            WHERE id = ?
        """, (emp_id,))

        row = cursor.fetchone()

        return (
            self._row_to_dict(row)
            if row else None
        )

    # ==================================================
    # CREATE
    # ==================================================

    def create(self, data):

        try:

            conn = get_connection()

            cursor = conn.cursor()

            emp_id = data.get("id")

            # ----------------------------------------------
            # VERIFICATION ID
            # ----------------------------------------------

            cursor.execute("""
                SELECT id
                FROM employes
                WHERE id = ?
            """, (emp_id,))

            exists = cursor.fetchone()

            if exists:

                conn.close()

                return None

            # ----------------------------------------------
            # INSERT
            # ----------------------------------------------

            cursor.execute("""

                INSERT INTO employes (

                    id,
                    nom,
                    prenom,
                    email,
                    telephone,
                    poste,
                    date_embauche,
                    salaire_base,
                    type_contrat,
                    date_fin_contrat,
                    heure_travail_jour,
                    adresse,
                    statut

                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """, (

                emp_id,

                data.get("nom"),

                data.get("prenom"),

                data.get("email"),

                data.get("telephone"),

                data.get("poste"),

                data.get("date_embauche"),

                data.get("salaire_base"),

                data.get("type_contrat"),

                data.get("date_fin_contrat"),

                data.get("heure_travail_jour"),

                data.get("adresse"),

                data.get("statut", "actif")

            ))

            conn.commit()

            conn.close()

            return emp_id

        except sqlite3.Error as e:

            print(
                f"Erreur création employé : {e}"
            )

            return None

    # ==================================================
    # UPDATE
    # ==================================================

    def update(self, emp_id, data):

        try:

            conn = get_connection()

            cursor = conn.cursor()

            cursor.execute("""
                UPDATE employes
                SET
                    nom=?,
                    prenom=?,
                    email=?,
                    telephone=?,
                    poste=?,
                    date_embauche=?,
                    salaire_base=?,
                    type_contrat=?,
                    date_fin_contrat=?,
                    heure_travail_jour=?,
                    adresse=?,
                    statut=?
                WHERE id=?
            """, (

                data.get("nom"),
                data.get("prenom"),
                data.get("email"),
                data.get("telephone"),
                data.get("poste"),
                data.get("date_embauche"),
                data.get("salaire_base"),
                data.get("type_contrat"),
                data.get("date_fin_contrat"),
                data.get("heure_travail_jour"),
                data.get("adresse"),
                data.get("statut"),
                emp_id

            ))

            conn.commit()

            success = cursor.rowcount > 0

            conn.close()

            return success

        except sqlite3.Error as e:

            print(
                "Erreur SQLite UPDATE :",
                str(e)
            )

            return False
    # ==================================================
    # DELETE
    # ==================================================

    def delete(self, emp_id):

        try:

            conn = get_connection()

            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM employes
                WHERE id = ?
                """,
                (emp_id,)
            )

            conn.commit()

            success = cursor.rowcount > 0

            conn.close()

            return success

        except sqlite3.Error as e:

            print(
                "Erreur SQLite DELETE :",
                str(e)
            )

            return False
    # ==================================================
    # SEARCH
    # ==================================================

    def search(self, term):

        cursor = self.conn.cursor()

        term = f"%{term}%"

        cursor.execute("""

            SELECT *
            FROM employes

            WHERE

                nom LIKE ?
                OR prenom LIKE ?
                OR email LIKE ?
                OR telephone LIKE ?
                OR poste LIKE ?

            ORDER BY id DESC

        """, (
            term,
            term,
            term,
            term,
            term
        ))

        rows = cursor.fetchall()

        return [
            self._row_to_dict(row)
            for row in rows
        ]

    # ==================================================
    # STATISTIQUES
    # ==================================================

    def get_statistiques(self):

        cursor = self.conn.cursor()

        # TOTAL

        cursor.execute("""
            SELECT COUNT(*)
            FROM employes
        """)

        total = cursor.fetchone()[0]

        # ACTIFS

        cursor.execute("""

            SELECT COUNT(*)
            FROM employes

            WHERE statut = 'actif'

        """)

        actifs = cursor.fetchone()[0]

        # SALAIRE TOTAL

        cursor.execute("""

            SELECT SUM(salaire_base)
            FROM employes

        """)

        total_salaire = (
                cursor.fetchone()[0]
                or 0
        )

        return {

            "total": total,

            "actifs": actifs,

            "total_salaire": total_salaire

        }

    # ==================================================
    # POSTES UNIQUES
    # ==================================================

    def get_postes_uniques(self):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT DISTINCT poste

            FROM employes

            WHERE poste IS NOT NULL
            AND poste != ''

        """)

        rows = cursor.fetchall()

        conn.close()

        return [
            row[0]
            for row in rows
        ]

    # ==================================================
    # FILTRE PAR POSTE
    # ==================================================

    def get_by_poste(self, poste):

        cursor = self.conn.cursor()

        cursor.execute("""

            SELECT *
            FROM employes

            WHERE poste = ?

            ORDER BY nom ASC

        """, (poste,))

        rows = cursor.fetchall()

        return [
            self._row_to_dict(row)
            for row in rows
        ]

    # ==================================================
    # ROW TO DICT
    # ==================================================

    def _row_to_dict(self, row):
        return {
            "id": row[0],
            "nom": row[1],
            "prenom": row[2],
            "email": row[3],
            "telephone": row[4],
            "poste": row[5],
            "date_embauche": row[6],
            "type_contrat": row[7],
            "date_fin_contrat": row[8],
            "heure_travail_jour": row[9],
            "salaire_base": row[10],
            "adresse": row[11],
            "statut": row[12],
        }
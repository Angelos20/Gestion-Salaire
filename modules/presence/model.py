from configuration.database import get_connection

def ajouter_presence(employe_id, date, heure_entree, heure_sortie, statut):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO presence (employe_id, date, heure_entree, heure_sortie, statut)
        VALUES (?, ?, ?, ?, ?)
    """, (employe_id, date, heure_entree, heure_sortie, statut))

    conn.commit()
    conn.close()


def get_presences():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, e.nom, e.poste, p.date, p.heure_entree, p.heure_sortie, p.statut
        FROM presence p
        JOIN employe e ON p.employe_id = e.id
    """)

    data = cursor.fetchall()
    conn.close()
    return data
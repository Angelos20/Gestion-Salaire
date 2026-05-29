#model presence
from configuration.database import get_connection
from modules.presence.controller import calcul_heures

def ajouter_presence(employe_id, date, heure_entree, heure_sortie, statut):
    conn = get_connection()
    cursor = conn.cursor()

    heure_travaillees = calcul_heures(heure_entree, heure_sortie)

    cursor.execute("""
        INSERT INTO presence (
            employe_id,
            date,
            heure_entree,
            heure_sortie,
            heure_travaillees,
            statut
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        employe_id,
        date,
        heure_entree,
        heure_sortie,
        heure_travaillees,
        statut
    ))

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
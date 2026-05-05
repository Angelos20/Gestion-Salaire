from configuration.database import get_connection

def get_config():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM configuration LIMIT 1")
    config = cursor.fetchone()

    conn.close()
    return config


def update_config(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE configuration SET
        heure_matin_debut = ?,
        heure_matin_fin = ?,
        heure_aprem_debut = ?,
        heure_aprem_fin = ?,
        heures_mensuelles = ?,
        penalite_retard = ?,
        penalite_depart = ?,
        taux_absence_jour = ?
        WHERE id = 1
    """, (
        data["matin_debut"],
        data["matin_fin"],
        data["aprem_debut"],
        data["aprem_fin"],
        data["heures_mensuelles"],
        data["penalite_retard"],
        data["penalite_depart"],
        data["taux_absence"]
    ))

    conn.commit()
    conn.close()
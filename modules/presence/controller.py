from datetime import datetime

def calcul_heures(heure_entree, heure_sortie):
    if not heure_entree or not heure_sortie:
        return 0

    fmt = "%H:%M"
    h1 = datetime.strptime(heure_entree, fmt)
    h2 = datetime.strptime(heure_sortie, fmt)

    diff = h2 - h1
    return round(diff.total_seconds() / 3600, 2)


def enregistrer_presence(employe_id, date, heure_entree, heure_sortie, statut):
    from configuration.database import get_connection

    heures = calcul_heures(heure_entree, heure_sortie)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO presence 
        (employe_id, date, heure_entree, heure_sortie, heure_travaillees, statut)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (employe_id, date, heure_entree, heure_sortie, heures, statut))

    conn.commit()
    conn.close()
from datetime import datetime
from configuration.database import get_connection

def get_employe(employe_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nom, prenom, poste, heure_travail_jour
        FROM employes
        WHERE id = ?
    """, (employe_id,))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def calcul_heures(heure_entree, heure_sortie):
    if not heure_entree or not heure_sortie:
        return 0

    fmt = "%H:%M"
    h1 = datetime.strptime(heure_entree, fmt)
    h2 = datetime.strptime(heure_sortie, fmt)

    return round((h2 - h1).total_seconds() / 3600, 2)


def calcul_statut(employe_id, heure_entree, heure_sortie):
    employe = get_employe(employe_id)

    if not employe:
        return "absent", 0

    heures_contract = employe["heure_travail_jour"] or 8

    heures_reelles = calcul_heures(heure_entree, heure_sortie)

    if heures_reelles <= 0:
        return "absent", 0

    ratio = heures_reelles / heures_contract

    if ratio >= 0.95:
        return "present", ratio
    elif ratio >= 0.70:
        return "retard", ratio
    else:
        return "absent_partiel", ratio
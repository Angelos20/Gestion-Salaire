#controller presence
from datetime import datetime

def calcul_heures(heure_entree, heure_sortie):
    if not heure_entree or not heure_sortie:
        return 0

    fmt = "%H:%M"
    h1 = datetime.strptime(heure_entree, fmt)
    h2 = datetime.strptime(heure_sortie, fmt)

    diff = h2 - h1
    return round(diff.total_seconds() / 3600, 2)

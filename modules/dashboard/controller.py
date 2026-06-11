from configuration.database import get_connection
from datetime import datetime


def get_kpis(date=None):
    conn = get_connection()
    cursor = conn.cursor()

    date = date or datetime.now().strftime("%Y-%m-%d")
    mois = date[:7]

    cursor.execute("SELECT COUNT(*) FROM employes")
    total_employes = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM presence WHERE date=? AND statut='present'", (date,))
    present = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM presence WHERE date=? AND statut='absent'", (date,))
    absent = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM presence WHERE date=? AND statut='retard'", (date,))
    retard = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*) FROM presence 
        WHERE date=? AND heure_sortie IS NOT NULL AND heure_sortie < '17:00'
    """, (date,))
    depart = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COALESCE(SUM(salaire_base),0) FROM employes")
    masse_salariale = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COALESCE(AVG(salaire_base),0) FROM employes")
    salaire_moyen = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COALESCE(SUM(salaire_net),0) FROM salaire WHERE mois=?", (mois,))
    total_paye = cursor.fetchone()[0] or 0

    taux_presence = (present / total_employes * 100) if total_employes else 0

    conn.close()

    def to_float(x):
        try:
            return float(str(x).replace(" ", "").replace(",", "."))
        except:
            return 0.0
    

    return {
        "employes": total_employes,
        "present": present,
        "absent": absent,
        "retard": retard,
        "depart": depart,
        "taux_presence": to_float(round(taux_presence, 2)),
        "masse_salariale": to_float(round(masse_salariale, 2)),
        "salaire_moyen": to_float(round(salaire_moyen, 2)),
        "total_paye": to_float(total_paye)
    }


def get_alertes(date=None):
    k = get_kpis(date)
    alertes = []

    if k["absent"] > 0:
        alertes.append(f"{k['absent']} absent(s)")
    if k["retard"] > 0:
        alertes.append(f"{k['retard']} retard(s)")
    if k["depart"] > 0:
        alertes.append(f"{k['depart']} départ(s)")
    if k["total_paye"] == 0:
        alertes.append("Aucune notification")

    return alertes


def get_recent_activities(date=None, limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    if date:
        cursor.execute("""
            SELECT message, date FROM activite
            WHERE DATE(date)=?
            ORDER BY date DESC LIMIT ?
        """, (date, limit))
    else:
        cursor.execute("""
            SELECT message, date FROM activite
            ORDER BY date DESC LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [f"{m} - {d}" for m, d in rows]

def log_activite(message=None, action=None, description=None,
                 module=None, utilisateur=None,
                 is_navigation=False):

    # 🚫 bloquer les logs de navigation
    if is_navigation:
        return

    conn = get_connection()
    cursor = conn.cursor()

    final_message = message or action or description or "Action inconnue"

    if utilisateur:
        final_message = f"[{utilisateur}] {final_message}"

    cursor.execute("""
        INSERT INTO activite (message, module, utilisateur, date)
        VALUES (?, ?, ?, ?)
    """, (
        final_message,
        module,
        utilisateur,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()
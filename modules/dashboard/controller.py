from configuration.database import get_connection
from datetime import datetime


def get_kpis(date=None):
    conn = get_connection()
    cursor = conn.cursor()

    # ✅ Utiliser la date sélectionnée
    date = date or datetime.now().strftime("%Y-%m-%d")
    mois = date[:7]  # extrait YYYY-MM

    # Employés
    cursor.execute("SELECT COUNT(*) FROM employes")
    total_employes = cursor.fetchone()[0]

    # Présence
    cursor.execute("SELECT COUNT(*) FROM presence WHERE date = ? AND statut = 'present'", (date,))
    present = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM presence WHERE date = ? AND statut = 'absent'", (date,))
    absent = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM presence WHERE date = ? AND statut = 'retard'", (date,))
    retard = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM presence 
        WHERE date = ? AND heure_sortie IS NOT NULL AND heure_sortie < '17:00'
    """, (date,))
    depart = cursor.fetchone()[0]

    # Salaire
    cursor.execute("SELECT SUM(salaire_base) FROM employes")
    masse_salariale = cursor.fetchone()[0] or 0

    cursor.execute("SELECT AVG(salaire_base) FROM employes")
    salaire_moyen = cursor.fetchone()[0] or 0

    # Paiement mensuel basé sur la date sélectionnée
    cursor.execute("SELECT SUM(salaire_net) FROM salaire WHERE mois = ?", (mois,))
    total_paye = cursor.fetchone()[0] or 0

    # KPI calculé
    taux_presence = (present / total_employes * 100) if total_employes else 0

    conn.close()

    return {
        "employes": total_employes,
        "present": present,
        "absent": absent,
        "retard": retard,
        "depart": depart,
        "taux_presence": round(taux_presence, 2),
        "masse_salariale": masse_salariale,
        "salaire_moyen": round(salaire_moyen, 2),
        "total_paye": total_paye
    }

def get_alertes(date=None):
    kpis = get_kpis(date)
    alertes = []

    if kpis["absent"] > 0:
        alertes.append(f"⚠️ {kpis['absent']} absent(s)")

    if kpis["retard"] > 0:
        alertes.append(f"⏱️ {kpis['retard']} retard(s)")

    if kpis["depart"] > 0:
        alertes.append(f"🚪 {kpis['depart']} départ(s) anticipé(s)")

    if kpis["total_paye"] == 0:
        alertes.append("💰 Aucun salaire payé")

    if not alertes:
        alertes.append("✅ Aucune alerte")

    return alertes

def get_recent_activities(date=None, limit=5):
    conn = get_connection()
    cursor = conn.cursor()

    if date:
        cursor.execute("""
            SELECT message, date
            FROM activite
            WHERE DATE(date) = ?
            ORDER BY date DESC
            LIMIT ?
        """, (date, limit))
    else:
        cursor.execute("""
            SELECT message, date
            FROM activite
            ORDER BY date DESC
            LIMIT ?
        """, (limit,))

    data = cursor.fetchall()
    conn.close()

    return [f"• {msg} - {dt}" for msg, dt in data]

def log_activite(message=None, action=None, description=None,
                 module=None, utilisateur=None):

    conn = get_connection()
    cursor = conn.cursor()

    # normalisation : on accepte message / action / description
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
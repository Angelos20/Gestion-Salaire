#model salaire
from configuration.database import get_connection
from datetime import datetime

# ─────────────────────────────
# EMPLOYÉS
# ─────────────────────────────
def get_employes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nom, prenom FROM employes")
    data = cursor.fetchall()

    conn.close()
    return data


def get_employe_by_id(emp_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nom, prenom FROM employes WHERE id=?", (emp_id,))
    data = cursor.fetchone()

    conn.close()
    return data

# ─────────────────────────────
# AVANCES
# ─────────────────────────────
def get_avances(employe_id, mois):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(montant), 0)
        FROM avances
        WHERE employe_id = ?
        AND strftime('%Y-%m', date) = ?
    """, (employe_id, mois))

    result = cursor.fetchone()[0]
    conn.close()

    return float(result or 0)

def get_avance_conf():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT plafond_avance, autoriser_avance
        FROM configuration
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    return result if result else (0, 0)
# ─────────────────────────────
# CONGÉS
# ─────────────────────────────
def get_conges(employe_id, mois, salaire_base):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date_debut, date_fin, paye
        FROM conges
        WHERE employe_id = ?
        AND strftime('%Y-%m', date_debut) = ?
    """, (employe_id, mois))

    conges = cursor.fetchall()
    conn.close()

    deduction = 0.0

    for debut, fin, paye in conges:
        if paye == 1:
            continue

        d1 = datetime.strptime(debut, "%Y-%m-%d")
        d2 = datetime.strptime(fin, "%Y-%m-%d")

        jours = (d2 - d1).days + 1
        deduction += jours * (float(salaire_base) / 30)

    return float(deduction)

def format_money(value):
    return f"{float(value or 0):,.0f}".replace(",", " ")

# ─────────────────────────────
# CALCUL + ENREGISTREMENT
# ─────────────────────────────
def calculer_salaire_complet(employe_id, mois, primes=0):
    from modules.salaire.controller import calculer_salaire

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            e.salaire_base,
            COALESCE(SUM(p.heure_travaillees), 0),
            COALESCE(SUM(CASE WHEN p.statut='absent' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN p.statut='retard' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN p.statut='partir tot' THEN 1 ELSE 0 END), 0),

            (
                SELECT COALESCE(SUM(a.montant), 0)
                FROM avances a
                WHERE a.employe_id = e.id
                AND substr(a.date, 1, 7) = ?
            ),

            (
                SELECT COALESCE(SUM(
                    (julianday(c.date_fin) - julianday(c.date_debut) + 1)
                    * (e.salaire_base / 30)
                ), 0)
                FROM conges c
                WHERE c.employe_id = e.id
                AND substr(c.date_debut, 1, 7) = ?
                AND c.paye = 0
            )

        FROM employes e
        LEFT JOIN presence p 
            ON p.employe_id = e.id 
            AND substr(p.date, 1, 7) = ?

        WHERE e.id = ?
        GROUP BY e.id
    """, (mois, mois, mois, employe_id))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    salaire_base = row[0]
    heures = row[1]
    retard = row[3]
    depart = row[4]
    avances = row[5]
    conges = row[6]

    result = calculer_salaire(
        salaire_base,
        heures,
        retard,
        depart,
        avances,
        conges,
        primes
    )

    return {
        "base": format_money(result["base"]),
        "salaire_reel": format_money(result["salaire_reel"]),
        "primes": format_money(primes),

        "deductions": format_money(result["deductions"]),
        "avances": format_money(avances),
        "conges": format_money(conges),

        "social_impot": format_money(result["social_impot"]),
        "net": format_money(result["net"])
    }

def enregistrer_salaire(employe_id, mois, data):
    conn = get_connection()
    cursor = conn.cursor()

    statut = data.get("statut", "EN_ATTENTE")

    cursor.execute("""
        INSERT INTO salaire (
            employe_id, mois,
            salaire_base,
            bonus,
            deduction,
            salaire_net,
            statut,
            date_paiement
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, date('now'))
        ON CONFLICT(employe_id, mois)
        DO UPDATE SET
            bonus=excluded.bonus,
            deduction=excluded.deduction,
            salaire_net=excluded.salaire_net,
            statut=excluded.statut,
            date_paiement=date('now')
    """, (
        employe_id,
        mois,
        format_money(data["base"]),
        format_money(data["primes"]),
        format_money(data["deductions"]),
        format_money(data["net"]),
        statut
    ))
    conn.commit()
    conn.close()

def get_salaire_paye(mois=None):
    conn = get_connection()
    cursor = conn.cursor()

    if mois:
        cursor.execute("""
            SELECT e.id, e.nom, e.prenom, s.mois,
                   s.salaire_base, s.bonus, s.deduction, s.salaire_net, s.statut
            FROM salaire s
            JOIN employes e ON e.id = s.employe_id
            WHERE s.mois = ?
        """, (mois,))
    else:
        cursor.execute("""
            SELECT e.id, e.nom, e.prenom, s.mois,
                   s.salaire_base, s.bonus, s.deduction, s.salaire_net, s.statut
            FROM salaire s
            JOIN employes e ON e.id = s.employe_id
        """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "nom": r[1],
            "prenom": r[2],
            "mois": r[3],
            "salaire_base": r[4],
            "bonus": r[5],
            "deduction": r[6],
            "salaire_net": r[7],
            "statut": r[8],
        }
        for r in rows
    ]
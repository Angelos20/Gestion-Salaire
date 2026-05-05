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

    cursor.execute("SELECT nom, prenom FROM employes WHERE id=?", (emp_id,))
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
        SELECT SUM(montant)
        FROM avances
        WHERE employe_id = ?
        AND strftime('%Y-%m', date) = ?
    """, (employe_id, mois))

    result = cursor.fetchone()[0]
    conn.close()

    return result or 0

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

    deduction = 0

    for debut, fin, paye in conges:
        if paye == 1:
            continue  # congé payé → pas de déduction

        d1 = datetime.strptime(debut, "%Y-%m-%d")
        d2 = datetime.strptime(fin, "%Y-%m-%d")

        jours = (d2 - d1).days + 1
        deduction += jours * (salaire_base / 30)

    return deduction

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

            -- présence
            COALESCE(SUM(p.heure_travaillees), 0),
            COALESCE(SUM(CASE WHEN p.statut='absent' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN p.statut='retard' THEN 1 ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN p.statut='partir tot' THEN 1 ELSE 0 END), 0),

            -- avances
            (
                SELECT COALESCE(SUM(a.montant), 0)
                FROM avances a
                WHERE a.employe_id = e.id
                AND substr(a.date, 1, 7) = ?
            ),

            -- congés
            (
                SELECT COALESCE(SUM(
                    CASE 
                        WHEN c.paye = 1 THEN 0
                        ELSE (julianday(c.date_fin) - julianday(c.date_debut) + 1) * (e.salaire_base / 30)
                    END
                ), 0)
                FROM conges c
                WHERE c.employe_id = e.id
                AND substr(c.date_debut, 1, 7) = ?
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
    absents = row[2]
    retard = row[3]
    depart = row[4]
    avances = row[5]
    conges = row[6]

    # 🔥 calcul présence UNIQUEMENT
    result = calculer_salaire(
        salaire_base,
        heures,
        absents,
        retard,
        depart,
        primes
    )

    # 🔥 séparation propre
    deductions_presence = result["deductions"]
    salaire_reel = result["salaire_reel"]

    # 🔥 TOTAL retenues
    total_deductions = deductions_presence + avances + conges

    # 🔥 NET FINAL UNIQUE (source unique)
    net_final = max(0, salaire_reel + primes - total_deductions)

    return {
        "base": salaire_base,
        "salaire_reel": salaire_reel,
        "primes": primes,

        # 🔥 détail important
        "deductions": deductions_presence,
        "avances": avances,
        "conges": conges,
        "total_deductions": total_deductions,

        "net": net_final
    }

def enregistrer_salaire(employe_id, mois, data):
    conn = get_connection()
    cursor = conn.cursor()

    statut = data.get("statut", "EN_ATTENTE")

    cursor.execute("""
        INSERT INTO salaire (
            employe_id,
            mois,
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
        data["base"],
        data["primes"],
        data["deductions"],
        data["net"],
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
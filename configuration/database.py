import sqlite3
from configuration.config import DB_PATH
from configuration.security import hash_password


# ─────────────────────────────────────────────
# CONNEXION
# ─────────────────────────────────────────────
def get_connection():
    return sqlite3.connect(DB_PATH)

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

    # Vérifier si config existe
    cursor.execute("SELECT id FROM configuration WHERE id = 1")
    exists = cursor.fetchone()

    if exists:
        # UPDATE
        cursor.execute("""
            UPDATE configuration SET
                heure_matin_debut = ?,
                heure_matin_fin = ?,
                heure_aprem_debut = ?,
                heure_aprem_fin = ?,

                heures_mensuelles = ?,
                taux_hsup = ?,

                penalite_retard = ?,
                penalite_depart = ?,
                tolerance_retard = ?,

                conges_par_mois = ?,
                autoriser_avance = ?,
                plafond_avance = ?,

                nom_entreprise = ?,
                adresse = ?,
                email = ?,
                telephone = ?,
                devise = ?,
                logo_path = ?

            WHERE id = 1
        """, (
            data["heure_matin_debut"],
            data["heure_matin_fin"],
            data["heure_aprem_debut"],
            data["heure_aprem_fin"],

            data["heures_mensuelles"],
            data["taux_hsup"],

            data["penalite_retard"],
            data["penalite_depart"],
            data["tolerance_retard"],

            data["conges_par_mois"],
            data["autoriser_avance"],
            data["plafond_avance"],

            data["nom_entreprise"],
            data["adresse"],
            data["email"],
            data["telephone"],
            data["devise"],
            data["logo_path"]
        ))

    else:
        # INSERT
        cursor.execute("""
            INSERT INTO configuration (
                id,
                heure_matin_debut,
                heure_matin_fin,
                heure_aprem_debut,
                heure_aprem_fin,

                heures_mensuelles,
                taux_hsup,

                penalite_retard,
                penalite_depart,
                tolerance_retard,

                conges_par_mois,
                autoriser_avance,
                plafond_avance,

                nom_entreprise,
                adresse,
                email,
                telephone,
                devise,
                logo_path
            )
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["heure_matin_debut"],
            data["heure_matin_fin"],
            data["heure_aprem_debut"],
            data["heure_aprem_fin"],

            data["heures_mensuelles"],
            data["taux_hsup"],

            data["penalite_retard"],
            data["penalite_depart"],
            data["tolerance_retard"],

            data["conges_par_mois"],
            data["autoriser_avance"],
            data["plafond_avance"],

            data["nom_entreprise"],
            data["adresse"],
            data["email"],
            data["telephone"],
            data["devise"],
            data["logo_path"]
        ))

    conn.commit()
    conn.close()
# ─────────────────────────────────────────────
# INITIALISATION DATABASE
# ─────────────────────────────────────────────
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ─── TABLE Activité ───────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activite (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            module TEXT,
            utilisateur TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    # ─── TABLE UTILISATEUR ───────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS utilisateur (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL UNIQUE,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        poste TEXT
    )
    """)

    # ─── TABLE EMPLOYE ───────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT ,
        email TEXT,
        telephone TEXT NOT NULL,
        poste TEXT,
        date_embauche TEXT,
        salaire_base REAL,
        adresse TEXT,
        statut TEXT
    )
    """)

    # ─── TABLE PRESENCE ──────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS presence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employe_id INTEGER,
        date TEXT,
        heure_entree TEXT,
        heure_sortie TEXT,
        heure_travaillees REAL,
        statut TEXT, -- present / absent / retard
        FOREIGN KEY (employe_id) REFERENCES employes(id)
    )
    """)

    # ─── TABLE SALAIRE ───────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS salaire (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employe_id INTEGER,
        mois TEXT,
        salaire_base REAL,
        bonus REAL DEFAULT 0,
        deduction REAL DEFAULT 0,
        salaire_net REAL,
        date_paiement TEXT,
        statut TEXT DEFAULT 'NON_PAYE',
        FOREIGN KEY (employe_id) REFERENCES employes(id),
        UNIQUE(employe_id, mois)
    )
    """)

    # ─── TABLE AVANCE ───────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS avances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employe_id INTEGER,
        montant REAL,
        date TEXT
    )
    """)

    # ─── TABLE CONGES ───────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employe_id INTEGER,
        date_debut TEXT,
        date_fin TEXT,
        type TEXT,
        paye INTEGER DEFAULT 1
    )
    """)

    # ─── TABLE CONFIGURATION ─────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        -- 🕒 HORAIRES
        heure_matin_debut TEXT,
        heure_matin_fin TEXT,
        heure_aprem_debut TEXT,
        heure_aprem_fin TEXT,

        -- 💰 SALAIRE
        heures_mensuelles REAL,
        taux_hsup REAL,

        -- ⚠️ PRÉSENCE
        penalite_retard REAL,
        penalite_depart REAL,
        tolerance_retard REAL,

        -- 🏖️ CONGÉS
        conges_par_mois REAL,
        autoriser_avance INTEGER,
        plafond_avance REAL,

        -- 🏢 ENTREPRISE
        nom_entreprise TEXT,
        adresse TEXT,
        email TEXT,
        telephone TEXT,
        devise TEXT,

        -- 🖼️ LOGO
        logo_path TEXT
    )
    """)

    conn.commit()
    conn.close()

    print("✅ Base de données initialisée avec succès !")


# ─────────────────────────────────────────────
# DONNÉES PAR DÉFAUT (OPTIONNEL MAIS UTILE)
# ─────────────────────────────────────────────
def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    # utilisateur admin par défaut
    cursor.execute("SELECT * FROM utilisateur WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO utilisateur (nom, username, email, password, poste)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "Administrateur",      # nom
            "admin",               # username
            "admin@example.com",   # email
            hash_password("admin123"),# password
            "Administrateur"
        ))

    conn.commit()
    conn.close()

    print("✅ Données initiales ajoutées !")
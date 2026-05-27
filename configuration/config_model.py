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
                   taux_hsup = ?,

                   penalite_retard = ?,
                   penalite_depart = ?,
                   tolerance_retard = ?,

                   conges_par_mois = ?,
                   autoriser_avance = ?,
                   plafond_avance = ?,
                   social_impot = ?,

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
        data["social_impot"],

        data["nom_entreprise"],
        data["adresse"],
        data["email"],
        data["telephone"],
        data["devise"],
        data["logo_path"]
    ))

    conn.commit()
    conn.close()
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from configuration.database import get_config
from reportlab.platypus import Image
import os


# ─────────────────────────────────────────────
# UTILITAIRE SAFE FLOAT
# ─────────────────────────────────────────────
def to_float(value):
    if value is None:
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        value = value.replace(" ", "").replace(",", "")
        try:
            return float(value)
        except:
            return 0.0

    return 0.0


def safe(v):
    return f"{to_float(v):,.0f}".replace(",", " ")


# ─────────────────────────────────────────────
# CALCUL SALAIRE
# ─────────────────────────────────────────────
def calculer_salaire(
        salaire_base,
        heures,
        retard,
        depart,
        avances,
        conges=0,
        primes=0
):

    config = get_config()
    if not config:
        raise Exception("Configuration introuvable")

    heures_mensuelles = config.get("heures_mensuelles", 173)
    penalite_retard_cfg = config.get("penalite_retard", 0)
    penalite_depart_cfg = config.get("penalite_depart", 0)
    social_impot_cfg = config.get("social_impot", 0)

    salaire_base = to_float(salaire_base)
    heures = to_float(heures)
    retard = to_float(retard)
    depart = to_float(depart)
    avances = to_float(avances)
    conges = to_float(conges)
    primes = to_float(primes)

    taux_horaire = salaire_base / heures_mensuelles if heures_mensuelles else 0

    salaire_reel = heures * taux_horaire

    penalite_retard = retard * penalite_retard_cfg
    penalite_depart = depart * penalite_depart_cfg

    social_impot = salaire_reel * (social_impot_cfg / 100)

    deductions = (
        penalite_retard +
        penalite_depart +
        social_impot +
        avances +
        conges
    )

    net = salaire_reel + primes - deductions

    return {
        "base": round(salaire_base, 3),
        "salaire_reel": round(salaire_reel, 3),
        "primes": round(primes, 3),

        "penalite_retard": round(penalite_retard, 3),
        "penalite_depart": round(penalite_depart, 3),
        "social_impot": round(social_impot, 3),

        "avances": round(avances, 3),
        "conges": round(conges, 3),

        "deductions": round(deductions, 3),
        "net": round(max(0, net), 3)
    }


# ─────────────────────────────────────────────
# BULLETIN PDF COMPLET
# ─────────────────────────────────────────────
def generer_bulletin_pdf(emp_id, nom, prenom, mois, data, filename="bulletin.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    config = get_config()

    nom_entreprise = config.get("nom_entreprise", "ENTREPRISE XYZ")
    logo_path = config.get("logo_path", None)

    elements = []  # ✅ DOIT ÊTRE EN PREMIER

    # ───── STYLE TITRE ─────
    title_style = ParagraphStyle(
        name="TitleCustom",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        textColor=colors.HexColor("#0A1628"),
        spaceAfter=20
    )

    # ───── LOGO (CORRIGÉ) ─────
    from reportlab.platypus import Image
    import os

    if logo_path and os.path.exists(logo_path):
        logo = Image(logo_path)
        logo.drawHeight = 60
        logo.drawWidth = 60
        elements.append(logo)

    # ───── TITRE ENTREPRISE ─────
    elements.append(Paragraph(nom_entreprise, title_style))
    elements.append(Paragraph("BULLETIN DE PAIE", title_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"Période : <b>{mois}</b>", styles["Normal"]))
    elements.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"]))
    elements.append(Spacer(1, 15))

    # ───── INFOS EMPLOYÉ ─────
    info_table = [
        ["Matricule", str(emp_id)],
        ["Nom & Prénom", f"{nom} {prenom}"],
    ]

    t1 = Table(info_table, colWidths=[150, 300])
    t1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#0A1628")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(t1)
    elements.append(Spacer(1, 15))

    # ───── NORMALISATION DATA ─────
    base = to_float(data.get("base"))
    salaire_reel = to_float(data.get("salaire_reel"))
    primes = to_float(data.get("primes"))
    avances = to_float(data.get("avances"))
    conges = to_float(data.get("conges"))
    deductions = to_float(data.get("deductions"))
    net = to_float(data.get("net"))

    penalites_impots = deductions - avances - conges

    # ───── TABLE SALAIRE ─────
    table_data = [
        ["DÉSIGNATION", "MONTANT (Ar)"],
        ["Salaire de base", safe(base)],
        ["Salaire réel", safe(salaire_reel)],
        ["Primes", safe(primes)],
        ["Avances", safe(avances)],
        ["Congés", safe(conges)],
        ["Pénalités + Impôts", safe(penalites_impots)],
        ["TOTAL RETENUES", safe(deductions)],
    ]

    t2 = Table(table_data, colWidths=[300, 150])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0A1628")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(t2)
    elements.append(Spacer(1, 20))

    # ───── NET ─────
    net_table = Table([
        ["NET À PAYER", f"{safe(net)} Ar"]
    ], colWidths=[300, 150])

    net_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1E6FD9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(net_table)
    elements.append(Spacer(1, 30))

    elements.append(Paragraph("Signature Employeur : ____________________", styles["Normal"]))
    elements.append(Paragraph("Signature Employé : ____________________", styles["Normal"]))

    doc.build(elements)
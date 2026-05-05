from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime


# ─────────────────────────────
# CALCUL SALAIRE (BASE PURE)
# ─────────────────────────────
def calculer_salaire(salaire_base, heures, absents, retard, depart, primes=0):
    taux_horaire = salaire_base / 173 if salaire_base else 0

    salaire_reel = heures * taux_horaire  # ✔ CORRECT

    penalite_absence = absents * (salaire_base / 30 if salaire_base else 0)
    penalite_retard = retard * 2000
    penalite_depart = depart * 2000

    deductions = penalite_absence + penalite_retard + penalite_depart

    salaire_net = salaire_reel + primes - deductions

    return {
        "base": salaire_base,
        "salaire_reel": salaire_reel,
        "primes": primes,
        "deductions": deductions,
        "salaire_net": salaire_net,
    }

# ─────────────────────────────
# BULLETIN PDF COMPLET
# ─────────────────────────────
def generer_bulletin_pdf(emp_id, nom, mois, data, filename="bulletin.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="TitleCustom",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        textColor=colors.HexColor("#0A1628"),
        spaceAfter=20
    )

    elements = []

    # ───────── TITRE ─────────
    elements.append(Paragraph("ENTREPRISE XYZ", title_style))
    elements.append(Paragraph("BULLETIN DE PAIE", title_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"Période : <b>{mois}</b>", styles["Normal"]))
    elements.append(Paragraph(f"Date : {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"]))
    elements.append(Spacer(1, 15))

    # ───────── INFOS EMPLOYÉ ─────────
    info_table = [
        ["Matricule", str(emp_id)],
        ["Nom & Prénom", f"{nom}"],
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

    # ───────── SALAIRE ─────────
    table_data = [
        ["DÉSIGNATION", "MONTANT (Ar)"],
        ["Salaire de base", f"{data.get('base', 0):,.0f}"],
        ["Salaire réel", f"{data.get('salaire_reel', 0):,.0f}"],
        ["Primes", f"{data.get('primes', 0):,.0f}"],
        ["Avances", f"{data.get('avances', 0):,.0f}"],
        ["Congés", f"{data.get('conges', 0):,.0f}"],
        ["Retenues présence", f"{data.get('deductions', 0):,.0f}"],
        ["TOTAL RETENUES",
         f"{data.get('deductions', 0) + data.get('avances', 0) + data.get('conges', 0):,.0f}"],
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

    # ───────── NET ─────────
    net = data.get("net", 0)

    net_table = Table([
        ["NET À PAYER", f"{net:,.0f} Ar"]
    ], colWidths=[300, 150])

    net_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1E6FD9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(net_table)
    elements.append(Spacer(1, 30))

    elements.append(Paragraph("Signature Employeur : ____________________", styles["Normal"]))
    elements.append(Paragraph("Signature Employé : ____________________", styles["Normal"]))

    doc.build(elements)
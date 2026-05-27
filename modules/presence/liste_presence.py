#liste presence

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QDateEdit, QComboBox,
    QAbstractItemView, QFileDialog, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from configuration.database import get_connection
import os
from modules.dashboard.controller import log_activite
from configuration.security import get_user
from configuration.audit_model import AuditModel

class ListePresence(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(self.getStyleSheet())

        self.setWindowTitle("Liste des Présences")
        self.setMinimumSize(1700, 800)
        self.setStyleSheet("background-color: #F5F7FA;")
        self.audit = AuditModel()

        self.init_ui()
        self.afficher_presences()

    # ---------------- UI ----------------
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # -------- Header --------
        header = QHBoxLayout()
        title = QLabel("📊 Liste des Présences")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1A2C3E;")
        header.addWidget(title)
        header.addStretch()
        style_btn = """
            QPushButton {
                        background-color: "#0A1640";
                        color: white;
                        font-weight: bold;
                        font-size : 15px ;
                        padding: 10px 20px;
                        border-radius: 5px;
                        font-family: sans-serif;
                    }
                QPushButton:hover   { background-color:"#1E6FD9"; }
                QPushButton:checked { background-color: "#0A1640"; }

        """

        self.btn_reset = QPushButton("♻ Restaurer")
        self.btn_reset.clicked.connect(self.vider_presences)
        self.btn_reset.setStyleSheet(style_btn)

        self.btn_export = QPushButton("📤 Exporter")
        self.btn_export.clicked.connect(self.exporter_fichier)
        self.btn_export.setStyleSheet(style_btn)

        header.addWidget(self.btn_reset)
        header.addWidget(self.btn_export)

        layout.addLayout(header)


        # -------- Filtres --------
        filtre_layout = QHBoxLayout()

        style_input = """
            QDateEdit, QComboBox {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 4px 8px;
                color: black;
            }
        """

        self.date_debut = QDateEdit()
        self.date_debut.setStyleSheet("color:black;font-family: sans serif;")
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDisplayFormat("dd/MM/yyyy")
        self.date_debut.setDate(QDate.currentDate().addDays(-7))
        self.date_debut.dateChanged.connect(self.afficher_presences)
        self.date_debut.setStyleSheet(style_input)

        self.date_fin = QDateEdit()
        self.date_fin.setStyleSheet("color:black;font-family: sans serif;")
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_fin.setDate(QDate.currentDate())
        self.date_fin.dateChanged.connect(self.afficher_presences)
        self.date_fin.setStyleSheet(style_input)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tous", "present", "absent", "retard", "depart"])
        self.status_filter.currentIndexChanged.connect(self.afficher_presences)
        self.status_filter.setStyleSheet(style_input)

        lbl_du = QLabel("Du :")
        lbl_au = QLabel("Au :")
        lbl_statut = QLabel("Statut :")
        lbl_au.setStyleSheet("color: black;")
        lbl_du.setStyleSheet("color: black;")
        lbl_statut.setStyleSheet("color: black;")

        filtre_layout.addWidget(lbl_du)
        filtre_layout.addWidget(self.date_debut)
        filtre_layout.addWidget(lbl_au)
        filtre_layout.addWidget(self.date_fin)
        filtre_layout.addWidget(lbl_statut)
        filtre_layout.addWidget(self.status_filter)

        filtre_layout.addStretch()
        layout.addLayout(filtre_layout)

        # -------- Tableau (STYLE INTACT) --------
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Prénom", "Poste", "Date",
            "Entrée", "Sortie", "Heures", "Statut"
        ])

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # ⚠️ TON STYLE ORIGINAL NON MODIFIÉ
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; color: black; border: 1px solid #C2D4E8; }
            QHeaderView::section { background-color: #0A1628; color: white; padding: 8px; font-weight: bold; }
            QTableWidget::item { padding: 5px; }
            QTableWidget::item:selected { background-color: #cce5ff; color: black; font-family: sans serif;}
            QTableWidget::item:focus { outline: none; }
        """)

        layout.addWidget(self.table)

    # ---------------- DATA ----------------
    def charger_presences(self):
        conn = get_connection()
        cursor = conn.cursor()

        debut = self.date_debut.date().toString("yyyy-MM-dd")
        fin = self.date_fin.date().toString("yyyy-MM-dd")
        statut = self.status_filter.currentText()

        query = """
            SELECT p.id, e.nom, e.prenom, e.poste, p.date,
                   p.heure_entree, p.heure_sortie,
                   p.heure_travaillees, p.statut
            FROM presence p
            LEFT JOIN employes e ON p.employe_id = e.id
            WHERE p.date BETWEEN ? AND ?
        """

        params = [debut, fin]

        if statut != "Tous":
            query += " AND p.statut = ?"
            params.append(statut)

        query += " ORDER BY p.date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    # ---------------- AFFICHAGE ----------------
    def afficher_presences(self):
        data = self.charger_presences()
        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, value in enumerate(row):

                # FORMAT DATE
                if j == 4 and value:
                    value = QDate.fromString(value, "yyyy-MM-dd").toString("dd/MM/yyyy")

                # FORMAT HEURE
                if j in [5, 6] and value:
                    value = value[:5]

                item = QTableWidgetItem(str(value) if value else "")
                item.setTextAlignment(Qt.AlignCenter)

                # 🔒 Couleur UNIQUEMENT colonne "Statut"
                if j == 8:
                    if value == "present":
                        item.setBackground(QColor("#4da6ff"))
                    elif value == "absent":
                        item.setBackground(QColor("#6699cc"))
                    elif value == "retard":
                        item.setBackground(QColor("#3399ff"))
                    elif value == "depart":
                        item.setBackground(QColor("#1a66cc"))

                self.table.setItem(i, j, item)

    # ---------------- RESET ----------------
    def vider_presences(self):

        # Dialogue de confirmation
        if self.show_dialog(
                "Confirmation",
                "Voulez-vous supprimer TOUTES les présences ?",
                icon="warning",
                yes_no=True
        ) == QDialog.Accepted:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM presence")
            conn.commit()
            conn.close()

            # refresh table
            self.afficher_presences()

            user = get_user()

            # AUDIT
            self.audit.log(
                action="DELETE_ALL",
                table="presence",
                record_id=None,
                old_data=None,
                new_data={"action": "Suppression totale des présences"},
                utilisateur=user["username"]
            )

            # LOG
            log_activite(
                "Suppression de la liste de présence réussie",
                module="presence",
                utilisateur=user["username"]
            )

            # SUCCESS DIALOG (stylé)
            self.show_dialog(
                "Succès",
                "Toutes les présences ont été supprimées avec succès.",
                icon="success"
            )
    # ---------------- EXPORT ----------------
    def exporter_fichier(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Exporter",
            os.path.join(os.path.expanduser("~"), "Documents"),  # <-- dossier Documents
            "Excel (*.xlsx);;PDF (*.pdf)"
        )

        if not file_path:
            return

        try:
            if "xlsx" in selected_filter:
                if not file_path.endswith(".xlsx"):
                    file_path += ".xlsx"
                self.export_excel(file_path)

                user = get_user()

                self.audit.log(
                    action="EXPORT_EXCEL",
                    table="presence",
                    record_id=None,
                    old_data=None,
                    new_data={"file": file_path},
                    utilisateur=user["username"]
                )


            elif "pdf" in selected_filter:

                if not file_path.endswith(".pdf"):
                    file_path += ".pdf"

                self.export_pdf(file_path)

                user = get_user()

                self.audit.log(

                    action="EXPORT_PDF",

                    table="presence",

                    record_id=None,

                    old_data=None,

                    new_data={"file": file_path},

                    utilisateur=user["username"]

                )

            self.show_dialog(
                "Succès",
                "Export réussi !",
                icon="success"
            )

            user = get_user()
            log_activite(
                f"Exportation de la liste de présence réussie",
                module="presence",
                utilisateur=user["username"]
            )


        except Exception as e:
            self.show_dialog(
                "Erreur",
                str(e),
                icon="error"
            )
    def export_excel(self, file_path):
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active

        headers = [
            self.table.horizontalHeaderItem(i).text()
            for i in range(self.table.columnCount())
        ]
        ws.append(headers)

        for row in range(self.table.rowCount()):
            data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                data.append(item.text() if item else "")
            ws.append(data)

        wb.save(file_path)

    def export_pdf(self, file_path):
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(file_path)

        data = [[
            self.table.horizontalHeaderItem(i).text()
            for i in range(self.table.columnCount())
        ]]

        for row in range(self.table.rowCount()):
            ligne = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                ligne.append(item.text() if item else "")
            data.append(ligne)

        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

        doc.build([table])

    def getStyleSheet(self):
        return """

           QPushButton {
                   background-color: "#0A1640";
                   color: white;
                   font-weight: bold;
                   font-size : 15px ;
                   padding: 10px 20px;
                   border-radius: 5px;
                   font-family: sans-serif;
               }
           QPushButton:hover   { background-color:"#1E6FD9"; }
           QPushButton:checked { background-color: "#0A1640"; }

           QLabel{
               color: black;
               font-size: 18px;
               font-family: sans-serif;
           }
           """

    def show_dialog(self, title, message, icon="info", yes_no=False):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumWidth(420)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 12px;
            }
            QLabel {
                color: #1A2C3E;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ICON
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFont(QFont("Segoe UI", 28))

        if icon == "success":
            icon_label.setText("✅")
        elif icon == "error":
            icon_label.setText("❌")
        elif icon == "warning":
            icon_label.setText("⚠️")
        else:
            icon_label.setText("ℹ️")

        layout.addWidget(icon_label)

        # MESSAGE
        msg = QLabel(message)
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        msg.setFont(QFont("Segoe UI", 11))
        layout.addWidget(msg)

        # BUTTONS
        btn_layout = QHBoxLayout()

        if yes_no:
            btn_no = QPushButton("Non")
            btn_yes = QPushButton("Oui")

            btn_no.setStyleSheet("""
                QPushButton {
                    background-color: #E5E7EB;
                    color: #111827;
                    padding: 8px 16px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #D1D5DB;
                }
            """)

            btn_yes.setStyleSheet("""
                QPushButton {
                    background-color: #0A1640;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #1E6FD9;
                }
            """)

            btn_yes.clicked.connect(dialog.accept)
            btn_no.clicked.connect(dialog.reject)

            btn_layout.addWidget(btn_no)
            btn_layout.addWidget(btn_yes)

        else:
            btn_ok = QPushButton("OK")
            btn_ok.setStyleSheet("""
                QPushButton {
                    background-color: #0A1640;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #1E6FD9;
                }
            """)
            btn_ok.clicked.connect(dialog.accept)
            btn_layout.addWidget(btn_ok)

        layout.addLayout(btn_layout)

        return dialog.exec()
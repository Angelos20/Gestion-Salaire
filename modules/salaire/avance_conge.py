#avance_congé.py

# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QDateEdit,
    QMessageBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView
)

from PySide6.QtCore import QDate, QDateTime
from PySide6.QtGui import QFont

from configuration.database import get_connection
from modules.salaire.model import get_employes,calcul_plafond_avance,calculer_jours_conges
from modules.dashboard.controller import log_activite
from configuration.audit_model import AuditModel
from configuration.security import get_user
from configuration.database import get_config

# ─────────────────────────────────────────────
# CLASSE
# ─────────────────────────────────────────────
class AvanceCongeForm(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion Avance & Congé")

        self.resize(1200, 700)

        self.audit = AuditModel()

        self.setStyleSheet("""
            background-color: #f8f9fa;
        """ + self.getStyleSheet())

        self._build()

    # ─────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────
    def _build(self):

        main_layout = QVBoxLayout(self)

        # =====================================
        # MENU
        # =====================================
        menu_layout = QHBoxLayout()

        self.btn_formulaire = QPushButton(
            "📝 Formulaire"
        )
        self.btn_formulaire.setStyleSheet(self.getStyleSheet())

        self.btn_avances = QPushButton(
            "💰 Liste Avances"
        )
        self.btn_avances.setStyleSheet(self.getStyleSheet())

        self.btn_conges = QPushButton(
            "🏖️ Liste Congés"
        )
        self.btn_conges.setStyleSheet(self.getStyleSheet())

        self.btn_formulaire.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )

        self.btn_avances.clicked.connect(
            lambda: self.stack.setCurrentIndex(1)
        )

        self.btn_conges.clicked.connect(
            lambda: self.stack.setCurrentIndex(2)
        )

        menu_layout.addWidget(self.btn_formulaire)
        menu_layout.addWidget(self.btn_avances)
        menu_layout.addWidget(self.btn_conges)

        main_layout.addLayout(menu_layout)

        # =====================================
        # STACKWIDGET
        # =====================================
        self.stack = QStackedWidget()

        main_layout.addWidget(self.stack)

        # =====================================
        # PAGE FORMULAIRE
        # =====================================
        self.page_formulaire = QWidget()

        self.stack.addWidget(self.page_formulaire)

        form_global_layout = QVBoxLayout(
            self.page_formulaire
        )

        form = QFormLayout()

        # EMPLOYE
        self.cb_employe = QComboBox()

        self.cb_employe.setStyleSheet(
            self.getStyleSheet()
        )

        self.employes = get_employes()

        for emp in self.employes:

            self.cb_employe.addItem(
                f"{emp[1]} {emp[2]}",
                emp[0]
            )

        self.emp = QLabel("Employé :")

        form.addRow(
            self.emp,
            self.cb_employe
        )

        # =====================================
        # AVANCE
        # =====================================
        self.titre_avance = QLabel(
            "💰 Avance"
        )

        self.titre_avance.setFont(
            QFont(
                "Segoe UI",
                12,
                QFont.Bold
            )
        )

        self.sb_avance = QDoubleSpinBox()

        self.sb_avance.setMaximum(
            10_000_000
        )

        self.sb_avance.setSuffix(" Ar")
        self.sb_avance.setStyleSheet(self.getStyleSheet())
        form.addRow(self.titre_avance)

        self.montant = QLabel("Montant :")
        self.montant.setStyleSheet(self.getStyleSheet())

        form.addRow(
            self.montant,
            self.sb_avance
        )

        self.btn_avance = QPushButton(
            "💾 Enregistrer Avance"
        )

        self.btn_avance.clicked.connect(
            self._save_avance
        )
        self.btn_avance.setStyleSheet(self.getStyleSheet())

        # =====================================
        # CONGE
        # =====================================
        self.titre_conge = QLabel(
            "🏖️ Congé"
        )

        self.titre_conge.setFont(
            QFont(
                "Segoe UI",
                12,
                QFont.Bold
            )
        )
        self.titre_conge.setStyleSheet(self.getStyleSheet())

        self.date_debut = QDateEdit()

        self.date_debut.setCalendarPopup(
            True
        )

        self.date_debut.setDate(
            QDate.currentDate()
        )

        self.date_debut.setDisplayFormat(
            "dd/MM/yyyy"
        )
        self.date_debut.setStyleSheet(self.getStyleSheet())

        self.date_fin = QDateEdit()

        self.date_fin.setCalendarPopup(
            True
        )

        self.date_fin.setDate(
            QDate.currentDate()
        )

        self.date_fin.setDisplayFormat(
            "dd/MM/yyyy"
        )
        self.date_fin.setStyleSheet(self.getStyleSheet())
        self.cb_type = QComboBox()

        self.cb_type.addItems([
            "payé",
            "non payé"
        ])
        self.cb_type.setStyleSheet(self.getStyleSheet())

        form.addRow(self.titre_conge)

        form.addRow(
            QLabel("Début :"),
            self.date_debut
        )

        form.addRow(
            QLabel("Fin :"),
            self.date_fin
        )

        form.addRow(
            QLabel("Type :"),
            self.cb_type
        )

        self.btn_conge = QPushButton(
            "💾 Enregistrer Congé"
        )
        self.btn_conge.setStyleSheet(self.getStyleSheet())

        self.btn_conge.clicked.connect(
            self._save_conge
        )


        # RESET
        self.btn_reset = QPushButton(
            "❌ Annuler"
        )
        self.btn_reset.setStyleSheet(self.getStyleSheet())

        self.btn_reset.clicked.connect(
            self._reset
        )

        # AJOUT
        btn_layout = QHBoxLayout()
        form_global_layout.addLayout(form)
        form_global_layout.addLayout(btn_layout)

        btn_layout.addWidget(
            self.btn_avance
        )

        btn_layout.addWidget(
            self.btn_conge
        )

        btn_layout.addWidget(
            self.btn_reset
        )

        # =====================================
        # PAGE AVANCES
        # =====================================
        self.page_avances = QWidget()

        self.stack.addWidget(self.page_avances)

        avance_layout = QVBoxLayout(
            self.page_avances
        )

        titre_avance = QLabel(
            "Liste des avances"
        )

        titre_avance.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Bold
            )
        )
        titre_avance.setStyleSheet(self.getStyleSheet())

        avance_layout.addWidget(
            titre_avance
        )

        self.table_avances = QTableWidget()

        self.table_avances.setColumnCount(5)

        self.table_avances.setHorizontalHeaderLabels([
            "ID",
            "Employé",
            "Montant",
            "Date",
            "Action"
        ])

        self.table_avances.horizontalHeader() \
            .setSectionResizeMode(
                QHeaderView.Stretch
        )

        self.table_avances.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table_avances.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.table_avances.setStyleSheet(self.getStyleSheet())

        avance_layout.addWidget(
            self.table_avances
        )

        self.btn_supprimer_toutes_avances = QPushButton(
            "🗑️ Supprimer toutes les avances"
        )
        self.btn_supprimer_toutes_avances.setStyleSheet(self.getStyleSheet())

        self.btn_supprimer_toutes_avances.clicked.connect(
            self.delete_all_avances
        )

        avance_layout.addWidget(
            self.btn_supprimer_toutes_avances
        )

        # =====================================
        # PAGE CONGES
        # =====================================
        self.page_conges = QWidget()

        self.stack.addWidget(self.page_conges)

        conge_layout = QVBoxLayout(
            self.page_conges
        )

        titre_conge = QLabel(
            "Liste des congés"
        )

        titre_conge.setFont(
            QFont(
                "Segoe UI",
                14,
                QFont.Bold
            )
        )
        titre_conge.setStyleSheet(self.getStyleSheet())

        conge_layout.addWidget(
            titre_conge
        )

        self.table_conges = QTableWidget()

        self.table_conges.setColumnCount(6)

        self.table_conges.setHorizontalHeaderLabels([
            "ID",
            "Employé",
            "Début",
            "Fin",
            "Type",
            "Action"
        ])

        self.table_conges.horizontalHeader() \
            .setSectionResizeMode(
                QHeaderView.Stretch
        )

        self.table_conges.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table_conges.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.table_conges.setStyleSheet(self.getStyleSheet())

        conge_layout.addWidget(
            self.table_conges
        )

        self.btn_supprimer_tous_conges = QPushButton(
            "🗑️ Supprimer tous les congés"
        )
        self.btn_supprimer_tous_conges.setStyleSheet(self.getStyleSheet())

        self.btn_supprimer_tous_conges.clicked.connect(
            self.delete_all_conges
        )

        conge_layout.addWidget(
            self.btn_supprimer_tous_conges
        )

        # LOAD
        self.load_avances()
        self.load_conges()

    # ─────────────────────────────────────────
    # LOAD AVANCES
    # ─────────────────────────────────────────
    def load_avances(self):

        self.table_avances.setRowCount(0)

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                a.id,
                e.nom,
                e.prenom,
                a.montant,
                a.date

            FROM avances a

            JOIN employes e
            ON e.id = a.employe_id

            ORDER BY a.id DESC
        """)

        rows = cursor.fetchall()

        for row_data in rows:

            row = self.table_avances.rowCount()

            self.table_avances.insertRow(row)

            self.table_avances.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(row_data[0])
                )
            )

            self.table_avances.setItem(
                row,
                1,
                QTableWidgetItem(
                    f"{row_data[1]} {row_data[2]}"
                )
            )

            self.table_avances.setItem(
                row,
                2,
                QTableWidgetItem(
                    f"{row_data[3]:,.0f} Ar"
                    .replace(",", " ")
                )
            )

            self.table_avances.setItem(
                row,
                3,
                QTableWidgetItem(
                    row_data[4]
                )
            )

            btn_delete = QPushButton(
                "Supprimer"
            )
            btn_delete.setStyleSheet("background-color: rgb(255, 0, 0);border-radius: none;")

            btn_delete.clicked.connect(
                lambda _, rid=row_data[0]:
                self.delete_avance(rid)
            )

            self.table_avances.setCellWidget(
                row,
                4,
                btn_delete
            )

        conn.close()

    # ─────────────────────────────────────────
    # LOAD CONGES
    # ─────────────────────────────────────────
    def load_conges(self):

        self.table_conges.setRowCount(0)

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                c.id,
                e.nom,
                e.prenom,
                c.date_debut,
                c.date_fin,
                c.paye

            FROM conges c

            JOIN employes e
            ON e.id = c.employe_id

            ORDER BY c.id DESC
        """)

        rows = cursor.fetchall()

        for row_data in rows:

            row = self.table_conges.rowCount()

            self.table_conges.insertRow(row)

            type_conge = (
                "Payé"
                if row_data[5]
                else "Non payé"
            )

            self.table_conges.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(row_data[0])
                )
            )

            self.table_conges.setItem(
                row,
                1,
                QTableWidgetItem(
                    f"{row_data[1]} {row_data[2]}"
                )
            )

            self.table_conges.setItem(
                row,
                2,
                QTableWidgetItem(
                    row_data[3]
                )
            )

            self.table_conges.setItem(
                row,
                3,
                QTableWidgetItem(
                    row_data[4]
                )
            )

            self.table_conges.setItem(
                row,
                4,
                QTableWidgetItem(
                    type_conge
                )
            )

            btn_delete = QPushButton(
                "Supprimer"
            )
            btn_delete.setStyleSheet("background-color: rgb(255, 0, 0);border-radius: none;")

            btn_delete.clicked.connect(
                lambda _, rid=row_data[0]:
                self.delete_conge(rid)
            )

            self.table_conges.setCellWidget(
                row,
                5,
                btn_delete
            )

        conn.close()

    # ─────────────────────────────────────────
    # SAVE AVANCE
    # ─────────────────────────────────────────
    def _save_avance(self):

        employe_id = self.cb_employe.currentData()

        montant = self.sb_avance.value()

        plafond = calcul_plafond_avance(employe_id)

        if montant > plafond:
            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText(f"Plafond dépassé ({plafond:,.0f} Ar)")
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(self.getStyleSheet())
            msg.exec()
            return

        date_time = QDateTime.currentDateTime() \
            .toString(
                "yyyy-MM-dd HH:mm:ss"
        )

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO avances (
                    employe_id,
                    montant,
                    date
                )
                VALUES (?, ?, ?)
            """, (
                employe_id,
                montant,
                date_time
            ))

            conn.commit()

            self.load_avances()

            self.sb_avance.setValue(0)

            user = get_user()

            log_activite(
                f"Avance enregistrée ({montant} Ar)",
                module="avance",
                utilisateur=user["username"]
            )

            msg = QMessageBox(self)
            msg.setWindowTitle("Succès")
            msg.setText(f"Avance de {employe_id} de {montant} enregistré avec succès !")
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet(self.getStyleSheet())
            msg.exec()

        except Exception as e:

            conn.rollback()

            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText(str(e))
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(self.getStyleSheet())
            msg.exec()

        finally:

            conn.close()

    # ─────────────────────────────────────────
    # SAVE CONGE
    # ─────────────────────────────────────────
    def _save_conge(self):

        employe_id = self.cb_employe.currentData()

        debut = self.date_debut.date() \
            .toString("yyyy-MM-dd")

        fin = self.date_fin.date() \
            .toString("yyyy-MM-dd")

        if self.date_fin.date() < \
                self.date_debut.date():

            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText("Dates invalides !")
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(self.getStyleSheet())
            msg.exec()

            return

        paye = 1 if \
            self.cb_type.currentText() == "payé" \
            else 0

        now = QDateTime.currentDateTime() \
            .toString(
                "yyyy-MM-dd HH:mm:ss"
        )

        config = get_config()

        # limite annuelle (fallback = 35 jours)
        limite = float(config.get("conges_annuels", 35))

        # année du congé
        annee = debut[:4]

        jours_existants = calculer_jours_conges(employe_id, annee)

        from datetime import datetime
        d1 = datetime.strptime(debut, "%Y-%m-%d")
        d2 = datetime.strptime(fin, "%Y-%m-%d")

        jours_nouveaux = (d2 - d1).days + 1

        if jours_existants + jours_nouveaux > limite:
            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText("Limite de congés mensuelle dépassée")
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(self.getStyleSheet())
            msg.exec()
            return

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO conges (
                    employe_id,
                    date_debut,
                    date_fin,
                    paye,
                    date_conge
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                employe_id,
                debut,
                fin,
                paye,
                now
            ))

            conn.commit()

            self.load_conges()

            user = get_user()

            log_activite(
                "Congé enregistré",
                module="conge",
                utilisateur=user["username"]
            )

            msg = QMessageBox(self)
            msg.setWindowTitle("Succès")
            msg.setText(f"Congé {employe_id} enregistré avec succès !")
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet(self.getStyleSheet())
            msg.exec()

        except Exception as e:

            conn.rollback()

            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText(str(e))
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet(self.getStyleSheet())
            msg.exec()

        finally:

            conn.close()

    # ─────────────────────────────────────────
    # DELETE AVANCE
    # ─────────────────────────────────────────
    def delete_avance(self, avance_id):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM avances
            WHERE id = ?
        """, (avance_id,))

        conn.commit()

        conn.close()

        self.load_avances()

        msg = QMessageBox(self)
        msg.setWindowTitle("Succès")
        msg.setText(f"Avance {avance_id} supprimé !")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(self.getStyleSheet())
        msg.exec()
    # ─────────────────────────────────────────
    # DELETE CONGE
    # ─────────────────────────────────────────
    def delete_conge(self, conge_id):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM conges
            WHERE id = ?
        """, (conge_id,))

        conn.commit()

        conn.close()

        self.load_conges()

        msg = QMessageBox(self)
        msg.setWindowTitle("Succès")
        msg.setText(f"Congé {conge_id} supprimé !")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(self.getStyleSheet())
        msg.exec()

    # ─────────────────────────────────────────
    # DELETE ALL AVANCES
    # ─────────────────────────────────────────
    def delete_all_avances(self):

        msg = QMessageBox(self)

        msg.setWindowTitle("Confirmation")

        msg.setText(
            "Supprimer toutes les avances ?"
        )

        yes = msg.addButton(
            "Oui",
            QMessageBox.YesRole
        )

        no = msg.addButton(
            "Non",
            QMessageBox.NoRole
        )
        msg.setIcon(QMessageBox.Question)
        msg.setDefaultButton(self.getStyleSheet())
        msg.exec()

        if msg.clickedButton() != yes:
            return

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM avances
        """)

        conn.commit()

        conn.close()

        self.load_avances()

        QMessageBox.information(
            self,
            "Succès",
            "Toutes les avances supprimées ✔"
        )

    # ─────────────────────────────────────────
    # DELETE ALL CONGES
    # ─────────────────────────────────────────
    def delete_all_conges(self):

        msg = QMessageBox(self)

        msg.setWindowTitle("Confirmation")

        msg.setText(
            "Supprimer tous les congés ?"
        )

        yes = msg.addButton(
            "Oui",
            QMessageBox.YesRole
        )

        no = msg.addButton(
            "Non",
            QMessageBox.NoRole
        )
        msg.setIcon(QMessageBox.Question)
        msg.setStyleSheet(self.getStyleSheet())
        msg.exec()

        if msg.clickedButton() != yes:
            return

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM conges
        """)

        conn.commit()

        conn.close()

        self.load_conges()

        QMessageBox.information(
            self,
            "Succès",
            "Tous les congés supprimés ✔"
        )

    # ─────────────────────────────────────────
    # RESET
    # ─────────────────────────────────────────
    def _reset(self):

        self.sb_avance.setValue(0)

        self.date_debut.setDate(
            QDate.currentDate()
        )

        self.date_fin.setDate(
            QDate.currentDate()
        )

        self.cb_type.setCurrentIndex(0)

        self.cb_employe.setCurrentIndex(0)

    # ─────────────────────────────────────────
    # STYLE
    # ─────────────────────────────────────────
    def getStyleSheet(self):

        return """

        QPushButton {
            background-color: #0A1640;
            color: white;
            font-weight: bold;
            font-size: 14px;
            padding: 10px 20px;
            border-radius: 8px;
            font-family: sans-serif;
        }

        QPushButton:hover {
            background-color: #1E6FD9;
        }

        QLabel {
            color: black;
            font-family: sans-serif;
            font-size: 14px;
        }

        QDateEdit,
        QComboBox,
        QDoubleSpinBox {
            background-color: white;
            border: 1px solid #D1D5DB;
            border-radius: 8px;
            padding: 8px;
            color: black;
            font-family: sans-serif;
        }

        QTableWidget {
            background-color: white;
            border: 1px solid #D1D5DB;
            color: black;
            gridline-color: #E5E7EB;
        }

        QHeaderView::section {
            background-color: #0A1640;
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }

        QStackedWidget {
            background-color: white;
            border-radius: 10px;
        }
        """
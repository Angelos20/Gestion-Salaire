from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel,
    QPushButton, QComboBox, QDoubleSpinBox,
    QDateEdit, QMessageBox
)
from PySide6.QtCore import QDate, QDateTime
from PySide6.QtGui import QFont

from configuration.database import get_connection
from modules.salaire.model import get_employes


class AvanceCongeForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Avance & Congé")
        self.resize(420, 320)
        self.setStyleSheet("background-color: #f8f9fa;")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.cb_employe = QComboBox()
        self.employes = get_employes()
        for emp in self.employes:
            self.cb_employe.addItem(f"{emp[1]} {emp[2]}", emp[0])

        form.addRow("Employé :", self.cb_employe)

        titre_avance = QLabel("💰 Avance")
        titre_avance.setFont(QFont("Segoe UI", 12, QFont.Bold))

        self.sb_avance = QDoubleSpinBox()
        self.sb_avance.setMaximum(10_000_000)
        self.sb_avance.setSuffix(" Ar")

        form.addRow(titre_avance)
        form.addRow("Montant :", self.sb_avance)

        btn_avance = QPushButton("💾 Enregistrer Avance")
        btn_avance.clicked.connect(self._save_avance)

        titre_conge = QLabel("🏖️ Congé")
        titre_conge.setFont(QFont("Segoe UI", 12, QFont.Bold))

        self.date_debut = QDateEdit()
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate())

        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate())

        self.cb_type = QComboBox()
        self.cb_type.addItems(["payé", "non payé"])

        form.addRow(titre_conge)
        form.addRow("Début :", self.date_debut)
        form.addRow("Fin :", self.date_fin)
        form.addRow("Type :", self.cb_type)

        btn_conge = QPushButton("💾 Enregistrer Congé")
        btn_conge.clicked.connect(self._save_conge)

        btn_reset = QPushButton("❌ Annuler")
        btn_reset.clicked.connect(self._reset)

        layout.addLayout(form)
        layout.addWidget(btn_avance)
        layout.addWidget(btn_conge)
        layout.addWidget(btn_reset)

    def _save_avance(self):
        employe_id = self.cb_employe.currentData()
        montant = self.sb_avance.value()

        if not employe_id or montant <= 0:
            QMessageBox.warning(self, "Erreur", "Données invalides")
            return

        date_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO avances (employe_id, montant, date) VALUES (?, ?, ?)",
                (employe_id, montant, date_time)
            )
            conn.commit()
            QMessageBox.information(self, "Succès", "Avance enregistrée ✔")
            self.sb_avance.setValue(0)

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Erreur", str(e))

        finally:
            conn.close()

    def _save_conge(self):
        employe_id = self.cb_employe.currentData()
        debut = self.date_debut.date().toString("yyyy-MM-dd")
        fin = self.date_fin.date().toString("yyyy-MM-dd")

        if self.date_fin.date() < self.date_debut.date():
            QMessageBox.warning(self, "Erreur", "Dates invalides")
            return

        paye = 1 if self.cb_type.currentText() == "payé" else 0
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO conges (employe_id, date_debut, date_fin, paye, date_enregistrement)
                VALUES (?, ?, ?, ?, ?)
            """, (employe_id, debut, fin, paye, now))

            conn.commit()
            QMessageBox.information(self, "Succès", "Congé enregistré ✔")

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Erreur", str(e))

        finally:
            conn.close()

    def _reset(self):
        self.sb_avance.setValue(0)
        self.date_debut.setDate(QDate.currentDate())
        self.date_fin.setDate(QDate.currentDate())
        self.cb_type.setCurrentIndex(0)
        self.cb_employe.setCurrentIndex(0)
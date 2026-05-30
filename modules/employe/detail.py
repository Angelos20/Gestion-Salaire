from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from configuration.audit_model import AuditModel
from configuration.security import get_user
from modules.dashboard.controller import log_activite

audit = AuditModel()


class EmployeDetail(QWidget):

    employe_modifie = Signal(dict)
    employe_supprime = Signal(int)

    def __init__(self, controller, employe):

        super().__init__()

        self.controller = controller
        self.employe = employe

        self.setWindowTitle(
            f"Détail - {employe['prenom']} {employe['nom']}"
        )

        self.setMinimumSize(600, 500)

        self.setStyleSheet("background-color: #F5F7FA;")

        self.init_ui()

    def init_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(20, 20, 20, 20)

        layout.setSpacing(15)

        # ================= HEADER =================

        header = QFrame()

        header.setStyleSheet(
            "background-color: white;"
            "border-radius: 12px;"
            "border: 1px solid #E5E7EB;"
        )

        header_layout = QVBoxLayout(header)

        id_lbl = QLabel(self.employe.get("id", ""))

        id_lbl.setFont(QFont("Segoe UI", 22, QFont.Bold))

        id_lbl.setAlignment(Qt.AlignCenter)

        id_lbl.setStyleSheet("color:black")

        header_layout.addWidget(id_lbl)

        nom = QLabel(
            f"{self.employe['nom']} {self.employe['prenom']}"
        )

        nom.setFont(QFont("Segoe UI", 22, QFont.Bold))

        nom.setAlignment(Qt.AlignCenter)

        nom.setStyleSheet("color:black")

        header_layout.addWidget(nom)

        poste = QLabel(
            self.employe.get("poste", "Non spécifié")
        )

        poste.setAlignment(Qt.AlignCenter)

        poste.setStyleSheet(
            "color: #6B7280; font-size: 22px;"
        )

        header_layout.addWidget(poste)

        layout.addWidget(header)

        # ================= INFOS =================

        info_frame = QFrame()

        info_frame.setStyleSheet(
            "background-color: white;"
            "border-radius: 12px;"
            "border: 1px solid #E5E7EB;"
        )

        info_layout = QVBoxLayout(info_frame)

        infos = [

            ("📧 Email", self.employe.get("email", "")),

            ("📞 Téléphone", self.employe.get("telephone", "")),

            ("📅 Embauche", self.employe.get("date_embauche", "")),

            (
                "💰 Salaire",
                f"{float(self.employe.get('salaire_base', 0) or 0):,.0f} Ar"
            ),
            ("📄 Contrat", self.employe.get("type_contrat", "")),

            ("📆 Fin contrat", self.employe.get("date_fin_contrat", "")),

            ("⏱ Heures/jour", self.employe.get("heure_travail_jour", "")),

            ("📊 Statut", self.employe.get("statut", "")),

            ("📍 Adresse", self.employe.get("adresse", "")),
        ]

        for label, value in infos:

            row = QHBoxLayout()

            lbl = QLabel(label)

            lbl.setStyleSheet(
                "min-width: 140px;"
                "color: #6B7280;"
                "font-weight: bold;"
            )

            val = QLabel(str(value))

            val.setStyleSheet("color: #1F2937;")

            val.setWordWrap(True)

            if label == "📊 Statut":

                color = "#10B981" if value == "actif" else "#EF4444"

                val.setStyleSheet(
                    f"color: {color}; font-weight: bold;"
                )

            row.addWidget(lbl)

            row.addWidget(val, 1)

            info_layout.addLayout(row)

        layout.addWidget(info_frame)

        # ================= BOUTONS =================

        btn_layout = QHBoxLayout()

        self.btn_modifier = QPushButton("Modifier")

        self.btn_modifier.setStyleSheet(self.getStyleSheet())

        self.btn_modifier.clicked.connect(self.modifier)

        btn_layout.addWidget(self.btn_modifier)

        self.btn_supprimer = QPushButton("Supprimer")

        self.btn_supprimer.setStyleSheet(self.getStyleSheet())

        self.btn_supprimer.clicked.connect(self.supprimer)

        btn_layout.addWidget(self.btn_supprimer)

        self.btn_fermer = QPushButton("Fermer")

        self.btn_fermer.setStyleSheet(self.getStyleSheet())

        self.btn_fermer.clicked.connect(self.close)

        btn_layout.addWidget(self.btn_fermer)

        layout.addLayout(btn_layout)

    # ==================================================
    # MODIFIER
    # ==================================================

    def modifier(self):

        from modules.employe.formulaire import EmployeFormulaire

        self.form = EmployeFormulaire(
            self.controller,
            self.employe
        )

        self.form.employe_sauvegarde.connect(
            self.on_modifie
        )

        self.form.show()

    def on_modifie(self, employe):

        self.employe = employe

        self.employe_modifie.emit(employe)

        self.close()

    # ==================================================
    # SUPPRESSION
    # ==================================================

    def supprimer(self):

        dialog = QDialog(self)

        dialog.setWindowTitle("Confirmation")

        dialog.setMinimumWidth(400)

        dialog.setStyleSheet(
            "background-color: white;"
            "border-radius: 10px;"
        )

        layout = QVBoxLayout(dialog)

        layout.setContentsMargins(20, 20, 20, 20)

        icon = QLabel("⚠️")

        icon.setFont(QFont("Segoe UI", 32))

        icon.setAlignment(Qt.AlignCenter)

        layout.addWidget(icon)

        msg = QLabel(
            f"Supprimer {self.employe['prenom']} "
            f"{self.employe['nom']} ?"
        )

        msg.setAlignment(Qt.AlignCenter)

        layout.addWidget(msg)

        btns = QHBoxLayout()

        btn_no = QPushButton("Non")

        btn_no.clicked.connect(dialog.reject)

        btn_yes = QPushButton("Oui")

        btn_yes.clicked.connect(dialog.accept)

        btns.addWidget(btn_no)

        btns.addWidget(btn_yes)

        layout.addLayout(btns)

        if dialog.exec() == QDialog.Accepted:

            old_data = dict(self.employe)

            result = self.controller.supprimer(
                self.employe["id"]
            )

            if result.get("success"):

                user = get_user()

                log_activite(
                    f"Suppression employé {self.employe['nom']}",
                    module="employe",
                    utilisateur=user["username"]
                )

                audit.log(
                    action="SUPPRESSION",
                    table="employes",
                    record_id=self.employe["id"],
                    old_data=old_data,
                    new_data=None,
                    utilisateur=user["username"]
                )

                QMessageBox.information(
                    self,
                    "Succès",
                    "Employé supprimé"
                )

                self.employe_supprime.emit(
                    self.employe["id"]
                )

                self.close()

            else:

                QMessageBox.warning(
                    self,
                    "Erreur",
                    result.get("error")
                )

    # ==================================================
    # STYLE
    # ==================================================

    def getStyleSheet(self):

        return """
        QPushButton {
            background-color: #0A1640;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            border: none;
        }

        QPushButton:hover {
            background-color: #1E6FD9;
        }

        QPushButton:pressed {
            background-color: #1E6FD9;
        }
        """
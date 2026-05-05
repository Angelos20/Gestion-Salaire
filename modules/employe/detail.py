from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox, QDialog,
    QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class EmployeDetail(QWidget):
    employe_modifie = Signal(dict)
    employe_supprime = Signal(int)

    def __init__(self, controller, employe):
        super().__init__()
        self.controller = controller
        self.employe = employe
        self.setWindowTitle(f"Détail - {employe['prenom']} {employe['nom']}")
        self.setMinimumSize(600, 500)
        self.setStyleSheet("background-color: #F5F7FA;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        # En-tête

        header = QFrame()
        header.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #E5E7EB;")
        header_layout = QVBoxLayout(header)
        nom = QLabel(f"{self.employe['nom']} {self.employe['prenom']}")
        nom.setFont(QFont("Segoe UI", 22, QFont.Bold))
        nom.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(nom)
        poste = QLabel(self.employe.get('poste', 'Non spécifié'))
        poste.setStyleSheet("color: #6B7280; font-size: 28px;")
        poste.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(poste)
        layout.addWidget(header)

        # Informations
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #E5E7EB;")
        info_layout = QVBoxLayout(info_frame)
        infos = [
            ("📧 Email", self.employe.get('email', 'Non renseigné')),
            ("📞 Téléphone", self.employe.get('telephone', 'Non renseigné')),
            ("📅 Date d'embauche", self.employe.get('date_embauche', 'Non renseignée')),
            ("💰 Salaire", f"{self.employe.get('salaire_base', 0):,.0f} Ar"),
            ("📊 Statut", self.employe.get('statut', 'actif')),
            ("📍 Adresse", self.employe.get('adresse', 'Non renseignée'))
        ]

        for label, value in infos:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("min-width: 110px; color: #6B7280; font-weight: bold;")
            val = QLabel(str(value))
            val.setStyleSheet("color: #1F2937;")
            val.setWordWrap(True)

            if label == "📊 Statut":
                color = "#10B981" if value == "actif" else "#EF4444"
                val.setStyleSheet(f"color: {color}; font-weight: bold;")

            row.addWidget(lbl)
            row.addWidget(val, 1)
            info_layout.addLayout(row)

        layout.addWidget(info_frame)

        # Boutons
        btn_layout = QHBoxLayout()
        #btn_layout.addStretch()
        self.btn_modifier = QPushButton("Modifier")
        self.btn_modifier.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            
            QPushButton:hover { background-color: #2563EB; }
        """)

        self.btn_modifier.clicked.connect(self.modifier)
        btn_layout.addWidget(self.btn_modifier)
        self.btn_supprimer = QPushButton("Supprimer")
        self.btn_supprimer.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }

            QPushButton:hover { background-color: #DC2626; }
        """)

        self.btn_supprimer.clicked.connect(self.supprimer)
        btn_layout.addWidget(self.btn_supprimer)
        self.btn_fermer = QPushButton("Fermer")
        self.btn_fermer.setStyleSheet("""
            QPushButton {
                background-color: #9CA3AF;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }

            QPushButton:hover { background-color: #6B7280; }
        """)

        self.btn_fermer.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_fermer)
        layout.addLayout(btn_layout)

    def modifier(self):
        from modules.employe.formulaire import EmployeFormulaire

        self.form = EmployeFormulaire(self.controller, self.employe)
        self.form.employe_sauvegarde.connect(self.on_modifie)
        self.form.show()

    def on_modifie(self, employe):
        self.employe = employe
        self.employe_modifie.emit(employe)
        self.close()

    def supprimer(self):

        # Créer une boîte de dialogue personnalisée
        dialog = QDialog(self)
        dialog.setWindowTitle("Confirmation de suppression")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("background-color: white; border-radius: 10px;")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Icône et message
        icon_label = QLabel("⚠️")
        icon_label.setFont(QFont("Segoe UI", 32))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        message = QLabel(f"Voulez-vous vraiment supprimer\n{self.employe['prenom']} {self.employe['nom']} ?")
        message.setFont(QFont("Segoe UI", 12))
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)

        layout.addWidget(message)
        avertissement = QLabel("Cette action est irréversible.")
        avertissement.setStyleSheet("color: #EF4444;")
        avertissement.setAlignment(Qt.AlignCenter)
        layout.addWidget(avertissement)

        # Boutons

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_non = QPushButton("Non, annuler")
        btn_non.setStyleSheet("""
            QPushButton {
                background-color: #9CA3AF;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                border: none;
            }

            QPushButton:hover { background-color: #6B7280; }
        """)

        btn_non.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_non)
        btn_oui = QPushButton("Oui, supprimer")
        btn_oui.setStyleSheet("""

            QPushButton {
                background-color: #EF4444;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                border: none;
            }

            QPushButton:hover { background-color: #DC2626; }
        """)

        btn_oui.clicked.connect(dialog.accept)
        btn_layout.addWidget(btn_oui)
        layout.addLayout(btn_layout)

        # Afficher la boîte de dialogue
        if dialog.exec() == QDialog.Accepted:
            result = self.controller.supprimer(self.employe['id'])

            if result.get('success'):
                QMessageBox.information(self, "Succès", "Employé supprimé avec succès!")
                self.employe_supprime.emit(self.employe['id'])
                self.close()

            else:
                QMessageBox.critical(self, "Erreur", f"Erreur: {result.get('error')}")
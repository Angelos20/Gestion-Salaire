from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDateEdit, QTextEdit, QFormLayout, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont
from resources.style import getStyleSheet
from modules.dashboard.controller import log_activite
from configuration.audit_model import AuditModel
from configuration.security import get_user

audit = AuditModel()

class EmployeFormulaire(QWidget):
    employe_sauvegarde = Signal(dict)

    def __init__(self, controller, employe=None):
        super().__init__()
        self.controller = controller
        self.employe = employe
        self.is_modification = employe is not None
        self.setWindowTitle("Modifier l'employé" if self.is_modification else "Ajouter un employé")
        self.setMinimumSize(500, 600)
        self.setStyleSheet("background-color: #F5F7FA;")
        self.setStyleSheet(getStyleSheet())
        self.init_ui()

        if self.employe:
            self.remplir()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Titre
        title = QLabel("Informations de l'employé")
        title.setFont(QFont("Segoe UI d", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white;")
        layout.addWidget(title)

        # Formulaire
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #E5E7EB;")
        form = QFormLayout(frame)
        form.setSpacing(12)
        form.setContentsMargins(20, 20, 20, 20)
        form.setLabelAlignment(Qt.AlignRight)

        # Champs
        self.lbl_id = QLabel("Identifiant *:")
        self.lbl_id.setStyleSheet(self.getStyleSheet())
        self.id = QLineEdit()
        self.id.setPlaceholderText("E-00001")
        self.id.setMinimumHeight(35)
        form.addRow(self.lbl_id, self.id)
        self.id.setStyleSheet(self.getStyleSheet())

        self.lbl_nom = QLabel("Nom *:")
        self.lbl_nom.setStyleSheet(self.getStyleSheet())
        self.nom = QLineEdit()
        self.nom.setPlaceholderText("Dupont")
        self.nom.setMinimumHeight(35)
        form.addRow(self.lbl_nom, self.nom)
        self.nom.setStyleSheet(self.getStyleSheet())

        self.lbl_prenom = QLabel("Prénom :")
        self.lbl_prenom.setStyleSheet(self.getStyleSheet())
        self.prenom = QLineEdit()
        self.prenom.setPlaceholderText("Jean")
        self.prenom.setMinimumHeight(35)
        form.addRow(self.lbl_prenom, self.prenom)
        self.prenom.setStyleSheet(self.getStyleSheet())

        self.lbl_email = QLabel("Email :")
        self.lbl_email.setStyleSheet(self.getStyleSheet())
        self.email = QLineEdit()
        self.email.setPlaceholderText("jean.dupont@email.com")
        self.email.setMinimumHeight(35)
        form.addRow(self.lbl_email, self.email)
        self.email.setStyleSheet(self.getStyleSheet())

        self.lbl_tel = QLabel("Téléphone *:")
        self.lbl_tel.setStyleSheet(self.getStyleSheet())
        self.tel = QLineEdit()
        self.tel.setPlaceholderText("+261 32 12 345 67")
        self.tel.setMinimumHeight(35)
        form.addRow(self.lbl_tel, self.tel)
        self.tel.setStyleSheet(self.getStyleSheet())

        self.lbl_poste = QLabel("Poste *:")
        self.lbl_poste.setStyleSheet(self.getStyleSheet())
        self.poste = QLineEdit()
        self.poste.setPlaceholderText("Développeur")
        self.poste.setMinimumHeight(35)
        form.addRow(self.lbl_poste, self.poste)
        self.poste.setStyleSheet(self.getStyleSheet())

        self.lbl_date = QLabel("Date d'embauche *:")
        self.lbl_date.setStyleSheet(self.getStyleSheet())
        self.date = QDateEdit()
        self.date.setDate(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd/MM/yyyy")
        self.date.setStyleSheet("color:black;font-family: sans-serif;")
        self.date.setMinimumHeight(35)
        form.addRow(self.lbl_date, self.date)


        self.lbl_salaire = QLabel("Salaire de base (Ar) *:")
        self.lbl_salaire.setStyleSheet(self.getStyleSheet())
        self.salaire = QLineEdit()
        self.salaire.setPlaceholderText("500000")
        self.salaire.setMinimumHeight(35)
        form.addRow(self.lbl_salaire, self.salaire)
        self.salaire.setStyleSheet(self.getStyleSheet())

        self.lbl_statut = QLabel("Statut:")
        self.lbl_statut.setStyleSheet(self.getStyleSheet())
        self.statut = QComboBox()
        self.statut.addItems(["actif", "inactif"])
        self.statut.setMinimumHeight(35)
        self.statut.setStyleSheet(self.getStyleSheet())
        form.addRow(self.lbl_statut, self.statut)

        self.lbl_adresse = QLabel("Adresse *:")
        self.lbl_adresse.setStyleSheet(self.getStyleSheet())
        self.adresse = QTextEdit()
        self.adresse.setMaximumHeight(80)
        self.adresse.setPlaceholderText("Adresse complète...")
        self.adresse.setMinimumHeight(60)
        self.adresse.setStyleSheet(self.getStyleSheet())
        form.addRow(self.lbl_adresse, self.adresse)

        layout.addWidget(frame)

        # Boutons
        btn_layout = QHBoxLayout()

        self.btn_save = QPushButton("Enregistrer")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setMinimumWidth(120)
        self.btn_save.setStyleSheet(self.getStyleSheet())
        self.btn_save.clicked.connect(self.sauvegarder)
        btn_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.setMinimumWidth(120)
        self.btn_cancel.setStyleSheet(self.getStyleSheet())
        self.btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def remplir(self):
        self.id.setText(self.employe.get('id', ''))
        self.nom.setText(self.employe.get('nom', ''))
        self.prenom.setText(self.employe.get('prenom', ''))
        self.email.setText(self.employe.get('email', ''))
        self.tel.setText(self.employe.get('telephone', ''))
        self.poste.setText(self.employe.get('poste', ''))
        self.salaire.setText(str(self.employe.get('salaire_base', 0)))
        idx = self.statut.findText(self.employe.get('statut', 'actif'))
        if idx >= 0:
            self.statut.setCurrentIndex(idx)
        self.adresse.setText(self.employe.get('adresse', ''))

    def sauvegarder(self):
        if not self.id.text() or not self.nom.text() or not self.tel.text() or not self.poste.text() or not self.salaire.text():
            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText("Veuillez remplir \n les champs obligatoires (*)")
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(self.styled_messagebox())

            msg.exec()
            return

        try:
            salaire = float(self.salaire.text() or 0)
        except ValueError:
            salaire = 0

        data = {
            'id': self.id.text(),
            'nom': self.nom.text(),
            'prenom': self.prenom.text(),
            'email': self.email.text(),
            'telephone': self.tel.text(),
            'poste': self.poste.text(),
            'date_embauche': self.date.date().toString("yyyy-MM-dd"),
            'salaire_base': salaire,
            'adresse': self.adresse.toPlainText(),
            'statut': self.statut.currentText()
        }

        if self.is_modification:

            # Anciennes données
            old_data = self.employe.copy()

            result = self.controller.modifier(self.employe['id'], data)

            log_activite(
                f"Modification employé ID {self.employe['id']}",
                module="employe",
                utilisateur="system"
            )

            user = get_user()

            audit.log(
                action="MODIFICATION",
                table="employes",
                record_id=data["id"],

                old_data=old_data,

                new_data=data,

                utilisateur=user["username"]
            )

        else:

            result = self.controller.ajouter(data)


            log_activite(
                f"Ajout nouvel employé {data['nom']} {data['prenom']}",
                module="employe",
                utilisateur="system"
            )

            user = get_user()

            audit.log(
                action="AJOUT",
                table="employes",
                record_id=data["id"],

                old_data=None,

                new_data=data,

                utilisateur=user["username"]
            )

        if result.get('success'):
            msg = QMessageBox(self)
            msg.setWindowTitle("Succès")
            msg.setText("Employé enregistré \n avec succès!")
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet(self.styled_messagebox())

            msg.exec()
            self.employe_sauvegarde.emit(result.get('employe', data))
            self.close()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText(f"Erreur: {result.get('error')}")
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(self.styled_messagebox())

            msg.exec()

            log_activite(
                f"Erreur sauvegarde employé: {result.get('error')}",
                module="employe",
                utilisateur="system"
            )

    def styled_messagebox(self):
        return """
        QMessageBox {
            background-color: #EDF3FB;
            font-size: 13px;
        }

        QLabel {
            color: #0A1628;
            font-size: 13px;
        }

        QPushButton {
            background-color: #1E6FD9;
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            min-width: 80px;
        }

        QPushButton:hover {
            background-color: #2A85FF;
        }
        """

    def getStyleSheet(self):
        return """
        
        QLabel {
            color: black;
            font-size: 14px;
            font-weight: bold;
            font-family: sans-serif;        
        }
        
        QLineEdit {
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ddd;
            color: black;
            font-family: sans-serif;
        }
        
        QTextEdit {
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ddd;
            color: black;
            font-family: sans-serif;
        }

        QLineEdit:focus {
            border: 1px solid #1877f2;
        }

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

        #btn_close {
            background: transparent;
            color: red;
            font-size: 20px;
        }
        #titre{
            color: black;
            font-size: 28px;
            font-weight: bold;
            font-family: sans-serif;
        }
        QComboBox {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 5px;
            background-color: white;
            color: black;  /* couleur du texte sélectionné */
            font-size: 14px;
            font-family: sans-serif;
        }
        QComboBox QAbstractItemView {
            background-color: white;  
            color: black;            
            selection-background-color: #1877f2;
            selection-color: black;            
        }
        QComboBox::drop-down {
            border: none;
        }
        
        QMessageBox {
                background-color: #F6F8FB;
                border-radius: 6px;
            }
            
            QMessageBox QLabel {
                color: #0A1640;
                font-size: 15px;
                font-weight: bold;
                font-family: sans-serif;
                min-width: 250px;
            }
            
            QMessageBox QPushButton {
                background-color: #0A1640;
                color: white;
                border-radius: 6px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }
            
            QMessageBox QPushButton:hover {
                background-color: #1E6FD9;
            }
            
            QMessageBox QPushButton:pressed {
                background-color: #163E73;
            }
        """
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QDateEdit,
    QTextEdit,
    QFormLayout,
    QMessageBox,
    QFrame,
    QSpinBox
)

from PySide6.QtCore import (
    Qt,
    QDate,
    Signal,
    QRegularExpression
)

from PySide6.QtGui import (
    QFont,
    QDoubleValidator,
    QRegularExpressionValidator
)


class EmployeFormulaire(QWidget):

    employe_sauvegarde = Signal(dict)

    def __init__(self, controller, employe=None):

        super().__init__()

        self.controller = controller
        self.employe = employe

        self.is_modification = employe is not None

        self.setWindowTitle(
            "Modifier l'employé"
            if self.is_modification
            else "Ajouter un employé"
        )

        self.setMinimumSize(1200, 750)

        self.setStyleSheet(self.getStyleSheet())

        self.init_ui()

        if self.employe:
            self.remplir()

    def init_ui(self):

        # ==================================================
        # MAIN LAYOUT
        # ==================================================

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(20, 20, 20, 20)

        main_layout.setSpacing(15)

        # ==================================================
        # TITRE
        # ==================================================

        title = QLabel("Informations de l'employé")

        title.setObjectName("titre")

        title.setAlignment(Qt.AlignCenter)

        title.setFont(QFont("Segoe UI", 18, QFont.Bold))

        main_layout.addWidget(title)

        # ==================================================
        # CONTENU PRINCIPAL
        # ==================================================

        content_layout = QVBoxLayout()

        content_layout.setSpacing(15)

        # ==================================================
        # ================= LIGNE 1 =========================
        # ==================================================

        row_1 = QHBoxLayout()

        row_1.setSpacing(15)

        # --------------------------------------------------
        # FRAME 1
        # --------------------------------------------------

        frame_1 = QFrame()

        form_1 = QFormLayout(frame_1)

        form_1.setContentsMargins(20, 20, 20, 20)

        form_1.setSpacing(12)

        # IDENTIFIANT

        self.lbl_id = QLabel("Identifiant *:")

        self.id = QLineEdit()

        self.id.setPlaceholderText("E-00001")

        self.id.setMinimumHeight(35)

        form_1.addRow(self.lbl_id, self.id)

        # NOM

        self.lbl_nom = QLabel("Nom *:")

        self.nom = QLineEdit()

        self.nom.setPlaceholderText("Dupont")

        self.nom.setMinimumHeight(35)

        form_1.addRow(self.lbl_nom, self.nom)

        # PRENOM

        self.lbl_prenom = QLabel("Prénom :")

        self.prenom = QLineEdit()

        self.prenom.setPlaceholderText("Jean")

        self.prenom.setMinimumHeight(35)

        form_1.addRow(self.lbl_prenom, self.prenom)

        # --------------------------------------------------
        # FRAME 2
        # --------------------------------------------------

        frame_2 = QFrame()

        form_2 = QFormLayout(frame_2)

        form_2.setContentsMargins(20, 20, 20, 20)

        form_2.setSpacing(12)

        # EMAIL

        self.lbl_email = QLabel("Email :")

        self.email = QLineEdit()

        self.email.setPlaceholderText("jean@email.com")

        self.email.setMinimumHeight(35)

        email_regex = QRegularExpression(
            r"^[\w\.-]+@[\w\.-]+\.\w+$"
        )

        email_validator = QRegularExpressionValidator(
            email_regex
        )

        self.email.setValidator(email_validator)

        form_2.addRow(self.lbl_email, self.email)

        # TELEPHONE

        self.lbl_tel = QLabel("Téléphone *:")

        self.tel = QLineEdit()

        self.tel.setPlaceholderText("+261 32 12 345 67")

        self.tel.setMinimumHeight(35)

        tel_regex = QRegularExpression(
            r"^\+?[0-9 ]{8,15}$"
        )

        tel_validator = QRegularExpressionValidator(
            tel_regex
        )

        self.tel.setValidator(tel_validator)

        form_2.addRow(self.lbl_tel, self.tel)

        # POSTE

        self.lbl_poste = QLabel("Poste *:")

        self.poste = QLineEdit()

        self.poste.setPlaceholderText("Développeur")

        self.poste.setMinimumHeight(35)

        form_2.addRow(self.lbl_poste, self.poste)

        # AJOUT LIGNE 1

        row_1.addWidget(frame_1)

        row_1.addWidget(frame_2)

        content_layout.addLayout(row_1)

        # ==================================================
        # ================= LIGNE 2 =========================
        # ==================================================

        row_2 = QHBoxLayout()

        row_2.setSpacing(15)

        # --------------------------------------------------
        # FRAME 3
        # --------------------------------------------------

        frame_3 = QFrame()

        form_3 = QFormLayout(frame_3)

        form_3.setContentsMargins(20, 20, 20, 20)

        form_3.setSpacing(12)

        # DATE EMBAUCHE

        self.lbl_date = QLabel("Date embauche *:")

        self.date = QDateEdit()

        self.date.setDate(QDate.currentDate())

        self.date.setCalendarPopup(True)

        self.date.setDisplayFormat("dd/MM/yyyy")

        self.date.setMinimumHeight(35)

        form_3.addRow(self.lbl_date, self.date)

        # SALAIRE

        self.lbl_salaire = QLabel("Salaire *:")

        self.salaire = QLineEdit()

        self.salaire.setPlaceholderText("500000")

        self.salaire.setMinimumHeight(35)

        salaire_validator = QDoubleValidator(
            0.0,
            999999999.99,
            2
        )

        self.salaire.setValidator(salaire_validator)

        form_3.addRow(
            self.lbl_salaire,
            self.salaire
        )

        # --------------------------------------------------
        # FRAME 4
        # --------------------------------------------------

        frame_4 = QFrame()

        form_4 = QFormLayout(frame_4)

        form_4.setContentsMargins(20, 20, 20, 20)

        form_4.setSpacing(12)

        # TYPE CONTRAT

        self.lbl_contrat = QLabel(
            "Type contrat *:"
        )

        self.type_contrat = QComboBox()

        self.type_contrat.addItems([
            "CDI",
            "CDD",
            "Stage",
            "Freelance",
            "Consultant"
        ])

        self.type_contrat.setMinimumHeight(35)

        form_4.addRow(
            self.lbl_contrat,
            self.type_contrat
        )

        # DATE FIN CONTRAT

        self.lbl_fin = QLabel(
            "Fin contrat :"
        )

        self.date_fin = QDateEdit()

        self.date_fin.setDate(
            QDate.currentDate()
        )

        self.date_fin.setCalendarPopup(True)

        self.date_fin.setDisplayFormat(
            "dd/MM/yyyy"
        )

        self.date_fin.setMinimumHeight(35)

        form_4.addRow(
            self.lbl_fin,
            self.date_fin
        )

        # HEURES TRAVAIL

        self.lbl_heure = QLabel(
            "Heures/jour :"
        )

        self.heure_travail = QSpinBox()

        self.heure_travail.setRange(1, 24)

        self.heure_travail.setValue(8)

        self.heure_travail.setMinimumHeight(35)

        form_4.addRow(
            self.lbl_heure,
            self.heure_travail
        )

        # AJOUT LIGNE 2

        row_2.addWidget(frame_3)

        row_2.addWidget(frame_4)

        content_layout.addLayout(row_2)

        # ==================================================
        # ================= LIGNE 3 =========================
        # ==================================================

        frame_5 = QFrame()

        form_5 = QFormLayout(frame_5)

        form_5.setContentsMargins(20, 20, 20, 20)

        form_5.setSpacing(12)

        # STATUT

        self.lbl_statut = QLabel("Statut :")

        self.statut = QComboBox()

        self.statut.addItems([
            "actif",
            "inactif"
        ])

        self.statut.setMinimumHeight(35)

        form_5.addRow(
            self.lbl_statut,
            self.statut
        )

        # ADRESSE

        self.lbl_adresse = QLabel("Adresse :")

        self.adresse = QTextEdit()

        self.adresse.setPlaceholderText(
            "Adresse complète..."
        )

        self.adresse.setMinimumHeight(120)

        form_5.addRow(
            self.lbl_adresse,
            self.adresse
        )

        content_layout.addWidget(frame_5)

        # ==================================================
        # AJOUT CONTENT
        # ==================================================

        main_layout.addLayout(content_layout)

        # ==================================================
        # BOUTONS
        # ==================================================

        btn_layout = QHBoxLayout()

        btn_layout.addStretch()

        self.btn_save = QPushButton(
            "Enregistrer"
        )

        self.btn_save.setMinimumHeight(40)

        self.btn_save.setMinimumWidth(130)

        self.btn_save.clicked.connect(
            self.sauvegarder
        )

        btn_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton(
            "Annuler"
        )

        self.btn_cancel.setMinimumHeight(40)

        self.btn_cancel.setMinimumWidth(130)

        self.btn_cancel.clicked.connect(
            self.close
        )

        btn_layout.addWidget(self.btn_cancel)

        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

        # ==================================================
        # GESTION CONTRAT
        # ==================================================

        self.type_contrat.currentTextChanged.connect(
            self.gerer_fin_contrat
        )

        self.gerer_fin_contrat()

    def gerer_fin_contrat(self):

        contrat = self.type_contrat.currentText()

        if contrat == "CDI":

            self.date_fin.setEnabled(False)

        else:

            self.date_fin.setEnabled(True)

    def remplir(self):

        self.id.setText(
            self.employe.get("id", "")
        )

        self.nom.setText(
            self.employe.get("nom", "")
        )

        self.prenom.setText(
            self.employe.get("prenom", "")
        )

        self.email.setText(
            self.employe.get("email", "")
        )

        self.tel.setText(
            self.employe.get("telephone", "")
        )

        self.poste.setText(
            self.employe.get("poste", "")
        )

        self.salaire.setText(
            str(
                self.employe.get(
                    "salaire_base",
                    0
                )
            )
        )

        self.adresse.setText(
            self.employe.get(
                "adresse",
                ""
            )
        )

        self.heure_travail.setValue(
            self.employe.get(
                "heure_travail",
                8
            )
        )

        idx = self.statut.findText(
            self.employe.get(
                "statut",
                "actif"
            )
        )

        if idx >= 0:

            self.statut.setCurrentIndex(idx)

        contrat_idx = self.type_contrat.findText(
            self.employe.get(
                "type_contrat",
                "CDI"
            )
        )

        if contrat_idx >= 0:

            self.type_contrat.setCurrentIndex(
                contrat_idx
            )

        date_fin = self.employe.get(
            "date_fin_contrat"
        )

        if date_fin:

            self.date_fin.setDate(
                QDate.fromString(
                    date_fin,
                    "yyyy-MM-dd"
                )
            )

    def sauvegarder(self):

        if (
                not self.id.text()
                or not self.nom.text()
                or not self.tel.text()
                or not self.poste.text()
                or not self.salaire.text()
        ):

            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez remplir tous les champs obligatoires."
            )

            return

        if self.email.text():

            if "@" not in self.email.text():

                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Email invalide."
                )

                return

        if len(
                self.tel.text().replace(" ", "")
        ) < 8:

            QMessageBox.warning(
                self,
                "Erreur",
                "Numéro téléphone invalide."
            )

            return

        data = {

            "id": self.id.text(),

            "nom": self.nom.text(),

            "prenom": self.prenom.text(),

            "email": self.email.text(),

            "telephone": self.tel.text(),

            "poste": self.poste.text(),

            "date_embauche":
                self.date.date().toString(
                    "yyyy-MM-dd"
                ),

            "salaire_base":
                float(self.salaire.text()),

            "type_contrat":
                self.type_contrat.currentText(),

            "date_fin_contrat":
                self.date_fin.date().toString(
                    "yyyy-MM-dd"
                )
                if self.type_contrat.currentText()
                   != "CDI"
                else None,

            "heure_travail":
                self.heure_travail.value(),

            "adresse":
                self.adresse.toPlainText(),

            "statut":
                self.statut.currentText()
        }

        self.employe_sauvegarde.emit(data)

        QMessageBox.information(
            self,
            "Succès",
            "Employé enregistré avec succès."
        )

        self.close()

    def getStyleSheet(self):

        return """

        QWidget {
            background-color: #F5F7FA;
        }

        QFrame {
            background-color: white;
            border-radius: 12px;
            border: 1px solid #E5E7EB;
        }

        QLabel {
            color: black;
            font-size: 14px;
            font-weight: bold;
            font-family: sans-serif;
            border: none;
        }

        QLineEdit,
        QTextEdit,
        QComboBox,
        QDateEdit,
        QSpinBox {

            padding: 8px;

            border-radius: 8px;

            border: 1px solid #ddd;

            background-color: white;

            color: black;

            font-size: 14px;

            font-family: sans-serif;
        }

        QLineEdit:focus,
        QTextEdit:focus,
        QComboBox:focus,
        QDateEdit:focus,
        QSpinBox:focus {

            border: 1px solid #1877f2;
        }

        QPushButton {

            background-color: #0A1640;

            color: white;

            font-weight: bold;

            font-size: 15px;

            padding: 10px 20px;

            border-radius: 5px;

            font-family: sans-serif;
        }

        QPushButton:hover {

            background-color: #1E6FD9;
        }

        #titre {

            color: black;

            font-size: 28px;

            font-weight: bold;

            font-family: sans-serif;
        }

        QMessageBox {

            background-color: #F6F8FB;
        }
        """

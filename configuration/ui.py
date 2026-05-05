from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel,
    QPushButton, QTimeEdit, QDoubleSpinBox,
    QMessageBox, QTabWidget, QCheckBox,
    QLineEdit, QFileDialog
)
from PySide6.QtCore import QTime, Qt
from PySide6.QtGui import QFont, QPixmap

from configuration.config_model import get_config, update_config


class ConfigRHView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚙️ Configuration RH Pro")
        self.setMinimumSize(950, 650)

        self.logo_path = None

        self._build()
        self._load()

    # ───────────────────────── STYLE ─────────────────────────
    def _style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F6F8FB;
                font-family: Segoe UI;
                font-size: 12px;
            }

            QLineEdit, QDoubleSpinBox, QTimeEdit {
                padding: 6px;
                border: 1px solid #D0D7E2;
                border-radius: 6px;
                background: white;
            }

            QLineEdit:focus, QDoubleSpinBox:focus, QTimeEdit:focus {
                border: 1px solid #1E6FD9;
            }

            QTabWidget::pane {
                border: 1px solid #D9E1EC;
                border-radius: 8px;
                background: white;
            }

            QTabBar::tab {
                background: #E9EEF5;
                padding: 10px;
                border-radius: 6px;
                margin: 2px;
            }

            QTabBar::tab:selected {
                background: #1E6FD9;
                color: white;
            }

            QPushButton {
                background-color: #1E6FD9;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1557b0;
            }
        """)

    # ───────────────────────── UI ─────────────────────────
    def _build(self):
        self._style()

        main = QVBoxLayout(self)

        title = QLabel("CONFIGURATION RH / PAIE")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main.addWidget(title)

        self.tabs = QTabWidget()

        self._tab_horaires()
        self._tab_salaire()
        self._tab_presence()
        self._tab_conges()
        self._tab_entreprise()

        main.addWidget(self.tabs)

        btn = QPushButton("💾 Enregistrer configuration")
        btn.setFixedHeight(45)
        btn.clicked.connect(self._save)

        main.addWidget(btn)

    # ───────────────────────── HORAIRES ─────────────────────────
    def _tab_horaires(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.matin_debut = QTimeEdit()
        self.matin_fin = QTimeEdit()
        self.aprem_debut = QTimeEdit()
        self.aprem_fin = QTimeEdit()

        for w in [self.matin_debut, self.matin_fin, self.aprem_debut, self.aprem_fin]:
            w.setDisplayFormat("HH:mm")

        layout.addRow("Matin début", self.matin_debut)
        layout.addRow("Matin fin", self.matin_fin)
        layout.addRow("Après-midi début", self.aprem_debut)
        layout.addRow("Après-midi fin", self.aprem_fin)

        self.tabs.addTab(tab, "🕒 Horaires")

    # ───────────────────────── SALAIRE ─────────────────────────
    def _tab_salaire(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.heures_mensuelles = QDoubleSpinBox()
        self.heures_mensuelles.setRange(0, 300)
        self.heures_mensuelles.setSuffix(" h/mois")
        self.heures_mensuelles.setToolTip("Heures normales de travail par mois (ex: 160)")

        self.taux_horaire = QDoubleSpinBox()
        self.taux_horaire.setRange(0, 10000000)
        self.taux_horaire.setSuffix(" Ar/h")
        self.taux_horaire.setToolTip("Salaire par heure")

        self.taux_hsup = QDoubleSpinBox()
        self.taux_hsup.setRange(1, 5)
        self.taux_hsup.setSingleStep(0.1)
        self.taux_hsup.setToolTip("Coefficient heures supplémentaires (ex: 1.5)")

        layout.addRow("Heures mensuelles", self.heures_mensuelles)
        layout.addRow("Taux horaire", self.taux_horaire)
        layout.addRow("HS coefficient", self.taux_hsup)

        self.tabs.addTab(tab, "💰 Salaire")

    # ───────────────────────── PRÉSENCE ─────────────────────────
    def _tab_presence(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.penalite_retard = QDoubleSpinBox()
        self.penalite_retard.setRange(0, 50000)
        self.penalite_retard.setSuffix(" Ar")

        self.penalite_depart = QDoubleSpinBox()
        self.penalite_depart.setRange(0, 50000)
        self.penalite_depart.setSuffix(" Ar")

        self.tolerance_retard = QDoubleSpinBox()
        self.tolerance_retard.setRange(0, 120)
        self.tolerance_retard.setSuffix(" min")

        layout.addRow("Pénalité retard", self.penalite_retard)
        layout.addRow("Pénalité départ", self.penalite_depart)
        layout.addRow("Tolérance retard", self.tolerance_retard)

        self.tabs.addTab(tab, "⚠️ Présence")

    # ───────────────────────── CONGÉS ─────────────────────────
    def _tab_conges(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.conges_par_mois = QDoubleSpinBox()
        self.conges_par_mois.setRange(0, 30)

        self.autoriser_avance = QCheckBox("Autoriser avances")

        self.plafond_avance = QDoubleSpinBox()
        self.plafond_avance.setRange(0, 10000000)
        self.plafond_avance.setSuffix(" Ar")

        layout.addRow("Congés/mois", self.conges_par_mois)
        layout.addRow("", self.autoriser_avance)
        layout.addRow("Plafond avance", self.plafond_avance)

        self.tabs.addTab(tab, "🏖️ Congés")

    # ───────────────────────── ENTREPRISE (LOGO) ─────────────────────────
    def _tab_entreprise(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.logo_label = QLabel("Aucun logo")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedHeight(120)
        self.logo_label.setStyleSheet("border: 1px dashed #999;")

        btn_logo = QPushButton("📁 Choisir Logo")
        btn_logo.clicked.connect(self._choose_logo)

        form = QFormLayout()

        self.nom_entreprise = QLineEdit()
        self.adresse = QLineEdit()
        self.email = QLineEdit()
        self.telephone = QLineEdit()
        self.devise = QLineEdit()

        form.addRow("Nom entreprise", self.nom_entreprise)
        form.addRow("Adresse", self.adresse)
        form.addRow("Email", self.email)
        form.addRow("Téléphone", self.telephone)
        form.addRow("Devise", self.devise)

        layout.addWidget(self.logo_label)
        layout.addWidget(btn_logo)
        layout.addLayout(form)

        self.tabs.addTab(tab, "🏢 Entreprise")

    # ───────────────────────── LOGO ─────────────────────────
    def _choose_logo(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Choisir logo", "", "Images (*.png *.jpg *.jpeg)"
        )

        if file:
            self.logo_path = file
            pix = QPixmap(file).scaled(120, 120, Qt.KeepAspectRatio)
            self.logo_label.setPixmap(pix)

    # ───────────────────────── LOAD ─────────────────────────
    def _load(self):
        try:
            config = get_config()
            if not config:
                return

            def g(i, default=0):
                return config[i] if len(config) > i and config[i] is not None else default

            self.matin_debut.setTime(QTime.fromString(g(1, "08:00"), "HH:mm"))
            self.matin_fin.setTime(QTime.fromString(g(2, "11:30"), "HH:mm"))
            self.aprem_debut.setTime(QTime.fromString(g(3, "14:30"), "HH:mm"))
            self.aprem_fin.setTime(QTime.fromString(g(4, "17:30"), "HH:mm"))

            self.heures_mensuelles.setValue(float(g(5)))
            self.taux_horaire.setValue(float(g(6)))
            self.taux_hsup.setValue(float(g(7, 1)))

            self.penalite_retard.setValue(float(g(8)))
            self.penalite_depart.setValue(float(g(9)))
            self.tolerance_retard.setValue(float(g(10)))

            self.conges_par_mois.setValue(float(g(11)))
            self.autoriser_avance.setChecked(bool(g(12)))
            self.plafond_avance.setValue(float(g(13)))

            self.nom_entreprise.setText(g(14, "Entreprise"))
            self.adresse.setText(g(15, ""))
            self.email.setText(g(16, ""))
            self.telephone.setText(g(17, ""))
            self.devise.setText(g(18, "Ar"))

        except Exception as e:
            QMessageBox.warning(self, "Erreur chargement", str(e))

    # ───────────────────────── SAVE ─────────────────────────
    def _save(self):
        try:
            data = {
                "heure_matin_debut": self.matin_debut.time().toString("HH:mm"),
                "heure_matin_fin": self.matin_fin.time().toString("HH:mm"),
                "heure_aprem_debut": self.aprem_debut.time().toString("HH:mm"),
                "heure_aprem_fin": self.aprem_fin.time().toString("HH:mm"),

                "heures_mensuelles": self.heures_mensuelles.value(),
                "taux_horaire": self.taux_horaire.value(),
                "taux_hsup": self.taux_hsup.value(),

                "penalite_retard": self.penalite_retard.value(),
                "penalite_depart": self.penalite_depart.value(),
                "tolerance_retard": self.tolerance_retard.value(),

                "conges_par_mois": self.conges_par_mois.value(),
                "autoriser_avance": int(self.autoriser_avance.isChecked()),
                "plafond_avance": self.plafond_avance.value(),

                "nom_entreprise": self.nom_entreprise.text(),
                "adresse": self.adresse.text(),
                "email": self.email.text(),
                "telephone": self.telephone.text(),
                "devise": self.devise.text(),

                "logo_path": self.logo_path or ""
            }

            update_config(data)

            QMessageBox.information(self, "Succès", "Configuration enregistrée")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
from PySide6.QtWidgets import (
    QComboBox, QWidget, QFrame, QLabel, QVBoxLayout,QHBoxLayout,
    QAbstractItemView, QTableWidgetItem, QPushButton,QLineEdit, QMessageBox,QTableWidget,
    QCheckBox, QTimeEdit, QFormLayout, QDoubleSpinBox, QTabWidget, QFileDialog,QHeaderView
)
from PySide6.QtCore import Qt,QTime, QSize
from PySide6.QtGui import (
    QPainter, QFont, QPainterPath, QPixmap, QIcon
)
from configuration.database import get_config, update_config, get_connection
from modules.dashboard.controller import log_activite
from configuration.audit_model import AuditModel
from configuration.security import get_user,hash_password
import os
import shutil

class ConfigRHView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚙️ Configuration RH Pro")
        self.setMinimumSize(950, 650)
        self.audit = AuditModel()

        self.logo_path = None

        self._build()
        self._load()

    def make_round_pixmap(self, image_path, size=120):

        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            return QPixmap()

        pixmap = pixmap.scaled(
            size,
            size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        rounded = QPixmap(size, size)
        rounded.fill(Qt.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addEllipse(0, 0, size, size)

        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)

        painter.end()

        return rounded

    # ───────────────────────── STYLE ─────────────────────────
    def _style(self):

        self.setStyleSheet("""

            QWidget{
                background-color: #F6F8FB;
                font-family: Segoe UI;
                font-size: 12px;
                color: black;
            }

            QLabel{
                color: #0A1640;
                background: transparent;
                font-weight: bold;
            }

            QLineEdit,
            QDoubleSpinBox,
            QTimeEdit,
            QTextEdit,
            QComboBox{

                background-color: white;
                border: 1px solid #C2D4E8;
                border-radius: 8px;
                padding: 8px;
                min-height: 18px;
            }

            QLineEdit:focus,
            QDoubleSpinBox:focus,
            QTimeEdit:focus{

                border: 2px solid #1E6FD9;
            }

            QTabWidget::pane{
                border: 1px solid #D9E1EC;
                border-radius: 10px;
                background: white;
            }

            QTabBar::tab{

                background: #E9EEF5;
                padding: 12px 18px;
                border-radius: 8px;
                margin: 3px;
                color: black;
                font-weight: bold;
            }

            QTabBar::tab:selected{

                background: #1E6FD9;
                color: white;
            }

            QPushButton{

                background-color: #0A1640;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 13px;
            }

            QPushButton:hover{
                background-color: #1E6FD9;
            }

            QPushButton:pressed{
                background-color: #163F7A;
            }

            QCheckBox{
                spacing: 10px;
                font-weight: bold;
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
        self._tab_utilisateur()
        self._tab_activite()

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
        self.matin_debut.setStyleSheet(self._style())
        self.matin_fin = QTimeEdit()
        self.matin_fin.setStyleSheet(self._style())
        self.aprem_debut = QTimeEdit()
        self.aprem_debut.setStyleSheet(self._style())
        self.aprem_fin = QTimeEdit()
        self.aprem_fin.setStyleSheet(self._style())

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
        self.heures_mensuelles.setStyleSheet(self._style())
        self.heures_mensuelles.setSuffix(" h/mois")
        self.heures_mensuelles.setToolTip("Heures normales de travail par mois (ex: 160)")

        self.taux_hsup = QDoubleSpinBox()
        self.taux_hsup.setRange(1, 5)
        self.taux_hsup.setSingleStep(0.1)
        self.taux_hsup.setStyleSheet(self._style())
        self.taux_hsup.setToolTip("Coefficient heures supplémentaires (ex: 1.5)")

        self.social_impot = QDoubleSpinBox()
        self.social_impot.setRange(1, 30)
        self.social_impot.setSingleStep(0.1)
        self.social_impot.setSuffix("%")
        self.social_impot.setStyleSheet(self._style())

        layout.addRow("Heures mensuelles", self.heures_mensuelles)
        layout.addRow("Heure Supplementaire coefficient", self.taux_hsup)
        layout.addRow("Social + impots", self.social_impot)

        self.tabs.addTab(tab, "💰 Salaire")

    # ───────────────────────── PRÉSENCE ─────────────────────────
    def _tab_presence(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.penalite_retard = QDoubleSpinBox()
        self.penalite_retard.setRange(0, 50000)
        self.penalite_retard.setSuffix(" Ar")
        self.penalite_retard.setStyleSheet(self._style())

        self.penalite_depart = QDoubleSpinBox()
        self.penalite_depart.setRange(0, 50000)
        self.penalite_depart.setSuffix(" Ar")
        self.penalite_depart.setStyleSheet(self._style())

        self.tolerance_retard = QDoubleSpinBox()
        self.tolerance_retard.setRange(0, 120)
        self.tolerance_retard.setSuffix(" min")
        self.tolerance_retard.setStyleSheet(self._style())

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
        self.conges_par_mois.setStyleSheet(self._style())

        self.autoriser_avance = QCheckBox("Autoriser avances")
        self.autoriser_avance.setStyleSheet(self._style())

        self.plafond_avance = QDoubleSpinBox()
        self.plafond_avance.setRange(0, 10000000)
        self.plafond_avance.setSuffix(" %")
        self.plafond_avance.setStyleSheet(self._style())

        layout.addRow("Nombre max des jours de Congés/an", self.conges_par_mois)
        layout.addRow("", self.autoriser_avance)
        layout.addRow("Plafond avance", self.plafond_avance)
        

        self.tabs.addTab(tab, "🏖️ Congés")

    # ───────────────────────── ENTREPRISE (LOGO) ─────────────────────────
    def _tab_entreprise(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.logo_label = QLabel()

        self.logo_label.setAlignment(Qt.AlignCenter)

        self.logo_label.setFixedSize(140, 140)

        self.logo_label.setStyleSheet("""

            QLabel{
                background-color: white;
                border-radius: 70px;
                border: 3px solid #1E6FD9;
            }

        """)

        btn_logo = QPushButton("📁 Choisir Logo")
        btn_logo.clicked.connect(self._choose_logo)
        btn_logo.setStyleSheet(self._style())

        form = QFormLayout()

        self.nom_entreprise = QLineEdit()
        self.nom_entreprise.setStyleSheet(self._style())
        self.adresse = QLineEdit()
        self.adresse.setStyleSheet(self._style())
        self.email = QLineEdit()
        self.email.setStyleSheet(self._style())
        self.telephone = QLineEdit()
        self.telephone.setStyleSheet(self._style())
        self.devise = QLineEdit()
        self.devise.setStyleSheet(self._style())

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

        # dossier par défaut = Pictures
        pictures_dir = os.path.expanduser("~/Pictures")

        file, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir logo",
            pictures_dir,
            "Images (*.png *.jpg *.jpeg)"
        )

        if file:
            # créer dossier data/logo s'il n'existe pas
            logo_dir = "data/logo"
            os.makedirs(logo_dir, exist_ok=True)

            # récupérer nom fichier
            filename = os.path.basename(file)

            # chemin destination
            destination = os.path.join(logo_dir, filename)

            # copier image dans projet
            shutil.copy(file, destination)

            # sauvegarder chemin
            self.logo_path = destination

            # afficher image
            pix = self.make_round_pixmap(destination, 130)

            self.logo_label.setPixmap(pix)

            user = get_user()

            log_activite(
                "Logo entreprise modifié",
                module="config",
                utilisateur=user["username"]
            )

            self.audit.log(
                action="UPDATE",
                table="configuration",
                record_id="logo",
                old_data=None,
                new_data={"logo_path": destination},
                utilisateur=user["username"]
            )
    # --------------------------UTILISATEUR---------------------
    def _tab_utilisateur(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.table_users = QTableWidget()
        self.table_users.setColumnCount(5)
        self.table_users.verticalHeader().setDefaultSectionSize(30)
        self.table_users.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_users.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_users.setFocusPolicy(Qt.NoFocus)
        self.table_users.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_users.setHorizontalHeaderLabels(
            ["ID", "Nom", "Username", "Email", "Poste"]
        )
        self.table_users.setStyleSheet("""
                            QTableWidget {
                                background-color: white;
                                color: black;
                                border: 1px solid #C2D4E8;
                            }

                            QHeaderView::section {
                                background-color: #0A1628;
                                color: white;
                                font-weight: bold;
                                border: none;
                            }

                            QTableWidget::item {
                                border: none;
                            }

                            /* Supprime effet de focus */
                            QTableWidget::item:focus {
                                outline: none;
                            }

                            /* Sélection propre */
                            QTableWidget::item:selected {
                                background-color: #cce5ff;
                                color: black;
                            }
                        """)
        btn_del = QPushButton("🗑 Supprimer")
        btn_upd = QPushButton("✏️ Modifier")

        btn_del.clicked.connect(self._delete_user)
        btn_upd.clicked.connect(self._update_user)

        layout.addWidget(self.table_users)
        layout.addWidget(btn_del)
        layout.addWidget(btn_upd)

        self._load_users()
        self.tabs.addTab(tab,"👤 Utilisateurs")


    def _load_users(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, nom, username, email, poste FROM utilisateur")
        rows = cur.fetchall()
        conn.close()

        self.table_users.setRowCount(len(rows))

        for r, u in enumerate(rows):
            for c in range(5):
                self.table_users.setItem(r, c, QTableWidgetItem(str(u[c])))

    def _delete_user(self):
        row = self.table_users.currentRow()
        if row == -1:
            return

        user = get_user()

        user_id = self.table_users.item(row, 0).text()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM utilisateur WHERE id=?", (user_id,))
        conn.commit()
        conn.close()

        log_activite(
            f"Suppression utilisateur ID {user_id}",
            module="config",
            utilisateur=user["username"]
        )

        self.audit.log(
            action="DELETE",
            table="utilisateur",
            record_id=user_id,
            old_data={"id": user_id},
            new_data=None,
            utilisateur=user["username"]
        )

        self._load_users()

    from PySide6.QtWidgets import QDialog

    def _update_user(self):

        row = self.table_users.currentRow()
        if row == -1:
            return

        user_id = self.table_users.item(row, 0).text()

        self.edit_window = UserEditorWindow(
            user_id=user_id,
            refresh_callback=self._load_users
        )
        self.edit_window.show()
    # -------------------------ACTIVITES----------------------
    def _tab_activite(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.table_logs = QTableWidget()
        self.table_logs.setColumnCount(5)
        self.table_logs.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_logs.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_logs.setFocusPolicy(Qt.NoFocus)
        self.table_logs.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_logs.setHorizontalHeaderLabels(
            ["ID", "Date", "Utilisateur", "Action", "Module"]
        )
        self.table_logs.setStyleSheet("""
                            QTableWidget {
                                background-color: white;
                                color: black;
                                border: 1px solid #C2D4E8;
                            }

                            QHeaderView::section {
                                background-color: #0A1628;
                                color: white;
                                font-weight: bold;
                                border: none;
                            }

                            QTableWidget::item {
                                border: none;
                            }

                            /* Supprime effet de focus */
                            QTableWidget::item:focus {
                                outline: none;
                            }

                            /* Sélection propre */
                            QTableWidget::item:selected {
                                background-color: #cce5ff;
                                color: black;
                            }
                        """)
        btn_del = QPushButton("🗑 Supprimer activité")
        btn_del.clicked.connect(self._delete_log)

        layout.addWidget(self.table_logs)
        layout.addWidget(btn_del)
        self._load_logs()
        self.tabs.addTab(tab, "Activités")

    def _load_logs(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, date, utilisateur, message, module
            FROM activite
            ORDER BY date DESC
        """)

        rows = cur.fetchall()
        conn.close()

        self.table_logs.setRowCount(len(rows))

        for r, l in enumerate(rows):
            for c in range(5):
                self.table_logs.setItem(r, c, QTableWidgetItem(str(l[c])))

    def _delete_log(self):
        row = self.table_logs.currentRow()
        if row == -1:
            return

        log_id = self.table_logs.item(row, 0).text()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM activite WHERE id=?", (log_id,))
        conn.commit()
        conn.close()

        self._load_logs()


    # ───────────────────────── LOAD ─────────────────────────
    def _load(self):
        try:
            config = get_config()

            if not config:
                return

            def g(key, default=0):
                return config[key] if key in config and config[key] is not None else default

            self.matin_debut.setTime(
                QTime.fromString(g("heure_matin_debut", "08:00"), "HH:mm")
            )

            self.matin_fin.setTime(
                QTime.fromString(g("heure_matin_fin", "11:30"), "HH:mm")
            )

            self.aprem_debut.setTime(
                QTime.fromString(g("heure_aprem_debut", "14:30"), "HH:mm")
            )

            self.aprem_fin.setTime(
                QTime.fromString(g("heure_aprem_fin", "17:30"), "HH:mm")
            )

            self.heures_mensuelles.setValue(
                float(g("heures_mensuelles", 160))
            )

            self.taux_hsup.setValue(
                float(g("taux_hsup", 1))
            )

            self.penalite_retard.setValue(
                float(g("penalite_retard", 0))
            )

            self.penalite_depart.setValue(
                float(g("penalite_depart", 0))
            )

            self.tolerance_retard.setValue(
                float(g("tolerance_retard", 0))
            )

            self.conges_par_mois.setValue(
                float(g("conges_par_mois", 0))
            )

            self.autoriser_avance.setChecked(
                bool(g("autoriser_avance", 0))
            )

            self.plafond_avance.setValue(
                float(g("plafond_avance", 0))
            )

            self.social_impot.setValue(
                float(g("social_impot", 0))
            )

            self.nom_entreprise.setText(
                g("nom_entreprise", "Entreprise")
            )

            self.adresse.setText(
                g("adresse", "")
            )

            self.email.setText(
                g("email", "")
            )

            self.telephone.setText(
                g("telephone", "")
            )

            self.devise.setText(
                g("devise", "Ar")
            )

            logo = g("logo_path", "")

            if logo and os.path.exists(logo):
                self.logo_path = logo

                pix = self.make_round_pixmap(logo, 130)

                self.logo_label.setPixmap(pix)

        except Exception as e:
            QMessageBox.warning(self, "Erreur chargement", str(e))

        log_activite(
            "Configuration chargée",
            module="config",
            utilisateur="system"
        )

    # ───────────────────────── SAVE ─────────────────────────
    def _save(self):
        try:
            data = {
                "heure_matin_debut": self.matin_debut.time().toString("HH:mm"),
                "heure_matin_fin": self.matin_fin.time().toString("HH:mm"),
                "heure_aprem_debut": self.aprem_debut.time().toString("HH:mm"),
                "heure_aprem_fin": self.aprem_fin.time().toString("HH:mm"),

                "heures_mensuelles": self.heures_mensuelles.value(),
                "taux_hsup": self.taux_hsup.value(),

                "penalite_retard": self.penalite_retard.value(),
                "penalite_depart": self.penalite_depart.value(),
                "tolerance_retard": self.tolerance_retard.value(),

                "conges_par_mois": self.conges_par_mois.value(),
                "autoriser_avance": int(self.autoriser_avance.isChecked()),
                "plafond_avance": self.plafond_avance.value(),
                "social_impot": self.social_impot.value(),

                "nom_entreprise": self.nom_entreprise.text(),
                "adresse": self.adresse.text(),
                "email": self.email.text(),
                "telephone": self.telephone.text(),
                "devise": self.devise.text(),

                "logo_path": self.logo_path or ""
            }

            update_config(data)

            user = get_user()

            log_activite(
                "Configuration mise à jour",
                module="config",
                utilisateur=user["username"]
            )

            self.audit.log(
                action="UPDATE",
                table="configuration",
                record_id="global",
                old_data=None,
                new_data=data,
                utilisateur=user["username"]
            )
            QMessageBox.information(self, "Succès", "Configuration enregistrée")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

class UserEditorWindow(QWidget):

    def __init__(self, user_id=None, refresh_callback=None):
        super().__init__()

        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.audit = AuditModel()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.old_pos = None

        self._apply_style()
        self._build()

        if self.user_id:
            self._load_user()

    # ───────────────────────── STYLE GLOBAL ─────────────────────────
    def _apply_style(self):
        self.setStyleSheet("""
            QWidget{
                background: transparent;
                font-family: Segoe UI;
            }

            QFrame{
                background-color: grey;
                border-radius: 20px;
            }

            QLabel{
                color: #0A1628;
                font-size: 13px;
                font-weight: bold;
            }

            QLineEdit, QComboBox{
                background-color: #F6F8FB;
                border: 1px solid #C2D4E8;
                border-radius: 8px;
                padding: 8px;
                min-height: 20px;
                color: black;
            }

            QLineEdit:focus, QComboBox:focus{
                border: 2px solid #1E6FD9;
            }

            QPushButton{
                background-color: #0A1628;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }

            QPushButton:hover{
                background-color: #1E6FD9;
            }
        """)

    # ───────────────────────── MESSAGEBOX STYLE ─────────────────────────
    def styled_messagebox(self):
        return """
        QMessageBox {
            background-color: #EDF3FB;
            font-size: 13px;
        }
        QLabel {
            color: #0A1628;
        }
        QPushButton {
            background-color: #1E6FD9;
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #2A85FF;
        }
        """

    # ───────────────────────── UI ─────────────────────────
    def _build(self):

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        self.card = QFrame()
        self.card.setFixedWidth(460)

        card_layout = QVBoxLayout(self.card)
        card_layout.setSpacing(10)

        # TOP BAR
        top_layout = QHBoxLayout()
        top_layout.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet("background:transparent;border:none;font-size:16px;")
        top_layout.addWidget(btn_close)

        # TITLE
        self.titre = QLabel("Modifier utilisateur" if self.user_id else "Ajouter utilisateur")
        self.titre.setAlignment(Qt.AlignCenter)
        self.titre.setStyleSheet("font-size:18px;")

        # INPUTS
        self.nom = QLineEdit()
        self.nom.setPlaceholderText("Nom complet")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Nom d'utilisateur")

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        pwd_layout = QHBoxLayout()
        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)

        self.btn_eye = QPushButton()
        self.btn_eye.setIcon(QIcon("./resources/icons/visible.png"))
        self.btn_eye.setIconSize(QSize(40, 40))
        self.btn_eye.setCheckable(True)
        self.btn_eye.clicked.connect(self.toggle_password)
        self.btn_eye.setStyleSheet("background: transparent; border: none;")

        pwd_layout.addWidget(self.password)
        pwd_layout.addWidget(self.btn_eye)

        self.conf_password = QLineEdit()
        self.conf_password.setPlaceholderText("Confirmer mot de passe")
        self.conf_password.setEchoMode(QLineEdit.Password)

        self.poste = QComboBox()
        self.poste.addItems([
            "Directeur", "Manager", "Employé",
            "Comptable", "RH", "Administrateur"
        ])

        # BUTTONS
        btn_layout = QHBoxLayout()

        self.btn_save = QPushButton("💾 Enregistrer")
        self.btn_save.clicked.connect(self._save)

        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.clicked.connect(self.close)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)

        # ASSEMBLAGE
        card_layout.addLayout(top_layout)
        card_layout.addWidget(self.titre)
        card_layout.addWidget(self.nom)
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.email)
        card_layout.addLayout(pwd_layout)
        card_layout.addWidget(self.conf_password)
        card_layout.addWidget(self.poste)
        card_layout.addLayout(btn_layout)

        main_layout.addWidget(self.card)

    # ───────────────────────── LOAD USER ─────────────────────────
    def _load_user(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT nom, username, email, poste
            FROM utilisateur
            WHERE id=?
        """, (self.user_id,))

        row = cur.fetchone()
        conn.close()

        if not row:
            QMessageBox.critical(self, "Erreur", "Utilisateur introuvable")
            self.close()
            return

        self.nom.setText(row["nom"])
        self.username.setText(row["username"])
        self.email.setText(row["email"])
        self.poste.setCurrentText(row["poste"] or "")

    # ───────────────────────── SAVE + AUDIT ─────────────────────────
    def _save(self):

        nom = self.nom.text().strip()
        username = self.username.text().strip()
        email = self.email.text().strip()
        poste = self.poste.currentText()

        if not nom or not username or not email:
            QMessageBox.warning(self, "Erreur", "Champs obligatoires")
            return

        conn = get_connection()
        cur = conn.cursor()
        user = get_user()

        try:

            # ───────── UPDATE ─────────
            if self.user_id:

                cur.execute("SELECT * FROM utilisateur WHERE id=?", (self.user_id,))
                old_data = dict(cur.fetchone())

                new_data = {
                    "nom": nom,
                    "username": username,
                    "email": email,
                    "poste": poste
                }

                cur.execute("""
                    UPDATE utilisateur
                    SET nom=?, username=?, email=?, poste=?
                    WHERE id=?
                """, (nom, username, email, poste, self.user_id))

                conn.commit()

                log_activite(
                    f"Modification utilisateur {self.user_id}",
                    module="config",
                    utilisateur=user["username"]
                )

                self.audit.log(
                    action="UPDATE",
                    table="utilisateur",
                    record_id=self.user_id,
                    old_data=old_data,
                    new_data=new_data,
                    utilisateur=user["username"]
                )

            # ───────── CREATE ─────────
            else:

                if self.password.text() != self.conf_password.text():
                    QMessageBox.warning(self, "Erreur", "Mots de passe différents")
                    return

                pwd = hash_password(self.password.text())

                cur.execute("""
                    INSERT INTO utilisateur (nom, username, email, password, poste)
                    VALUES (?, ?, ?, ?, ?)
                """, (nom, username, email, pwd, poste))

                conn.commit()

                self.audit.log(
                    action="INSERT",
                    table="utilisateur",
                    record_id=username,
                    old_data=None,
                    new_data={
                        "nom": nom,
                        "username": username,
                        "email": email,
                        "poste": poste
                    },
                    utilisateur=user["username"]
                )

                log_activite(
                    "Création utilisateur",
                    module="config",
                    utilisateur=user["username"]
                )

            if self.refresh_callback:
                self.refresh_callback()

            msg = QMessageBox(self)
            msg.setWindowTitle("Succès")
            msg.setText("Opération réussie")
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet(self.styled_messagebox())
            msg.exec()

            self.close()

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Erreur", str(e))

        finally:
            conn.close()

    def toggle_password(self):
        if self.btn_eye.isChecked():
            self.password.setEchoMode(QLineEdit.Normal)
            self.conf_password.setEchoMode(QLineEdit.Normal)
            self.btn_eye.setIcon(QIcon("./resources/icons/hide.png"))
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.conf_password.setEchoMode(QLineEdit.Password)
            self.btn_eye.setIcon(QIcon("./resources/icons/visible.png"))

    # ───────────────────────── DRAG ─────────────────────────
    def mousePressEvent(self, event):
        self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
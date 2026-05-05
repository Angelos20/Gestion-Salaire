import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QFrame, QHBoxLayout, QGraphicsOpacityEffect, QMessageBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, QSize
from PySide6.QtGui import QIcon

from configuration.database import get_connection
from configuration.security import verify_password, set_user
from .signup import PageSignUp
from modules.dashboard.controller import log_activite
from resources.style import getStyleSheet


class PageLogin(QWidget):
    def __init__(self):
        super().__init__()

        # 🎨 style global
        self.setStyleSheet(getStyleSheet())

        # 🔐 sécurité login
        self.attempts = 0
        self.max_attempts = 3
        self.block_time = 30
        self.blocked_until = 0

        # fenêtre
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.old_pos = None

        # ───────── UI ─────────
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        self.card = QFrame()
        self.card.setFixedWidth(460)
        self.card.setStyleSheet("""QFrame {background-color: white; border-radius: 20px;}""")

        card_layout = QVBoxLayout()

        # ───────── TOP ─────────
        top_layout = QHBoxLayout()
        top_layout.addStretch()

        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("btn_close")
        self.btn_close.clicked.connect(self.close)


        top_layout.addWidget(self.btn_close)

        # ───────── TITRE ─────────
        self.titre = QLabel("Connexion")
        self.titre.setAlignment(Qt.AlignCenter)
        self.titre.setObjectName("titre")

        # ───────── INPUTS ─────────
        self.username = QLineEdit()
        self.username.setPlaceholderText("Nom d'utilisateur")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)

        # password toggle
        self.btn_eye = QPushButton()
        self.btn_eye.setIcon(QIcon("./resources/icons/visible.png"))
        self.btn_eye.setStyleSheet("background-color: transparent;")
        self.btn_eye.setIconSize(QSize(40, 40))
        self.btn_eye.setCheckable(True)
        self.btn_eye.clicked.connect(self.toggle_password)

        mdp_layout = QHBoxLayout()
        mdp_layout.addWidget(self.password)
        mdp_layout.addWidget(self.btn_eye)

        # ───────── BUTTONS ─────────
        btn_layout = QHBoxLayout()

        self.btn_login = QPushButton("Se connecter")
        self.btn_cancel = QPushButton("Annuler")

        btn_layout.addWidget(self.btn_login)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_signup = QPushButton("S'inscrire")
        self.btn_signup.clicked.connect(self.signup)

        # ───────── ASSEMBLAGE ─────────
        card_layout.addLayout(top_layout)
        card_layout.addWidget(self.titre)
        card_layout.addWidget(self.username)
        card_layout.addLayout(mdp_layout)
        card_layout.addLayout(btn_layout)
        card_layout.addWidget(self.btn_signup)

        self.card.setLayout(card_layout)
        main_layout.addWidget(self.card)
        self.setLayout(main_layout)

        # ───────── ACTIONS ─────────
        self.btn_login.clicked.connect(self.login_action)
        self.btn_cancel.clicked.connect(self.clear_fields)
        self.password.returnPressed.connect(self.login_action)

    # ───────── LOGIN ─────────
    def login_action(self):

        # 🚫 blocage actif
        if time.time() < self.blocked_until:
            remaining = int(self.blocked_until - time.time())

            QMessageBox.warning(
                self,
                "Bloqué",
                f"Trop de tentatives. Réessaie dans {remaining} secondes"
            )

            log_activite(
                f"Tentative bloquée ({remaining}s restant)",
                module="security",
                utilisateur=self.username.text().strip()
            )
            return

        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Champs vides")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM utilisateur WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        conn.close()

        # ❌ utilisateur introuvable
        if not user:
            self.fail_login(username, "Utilisateur introuvable")
            return

        # ❌ mot de passe incorrect
        if not verify_password(password, user[4]):
            self.fail_login(username, "Mot de passe incorrect")
            return

        # ✔ succès login
        self.attempts = 0
        set_user(user)

        log_activite(
            message="Connexion réussie",
            module="auth",
            utilisateur=username
        )

        QMessageBox.information(self, "Succès", "Connexion réussie")
        self.open_accueil()

    # ───────── FAIL LOGIN ─────────
    def fail_login(self, username, reason):

        self.attempts += 1

        log_activite(
            message=f"Échec connexion ({reason})",
            module="auth",
            utilisateur=username
        )

        QMessageBox.critical(self, "Erreur", reason)

        # 🔒 blocage après 3 tentatives
        if self.attempts >= self.max_attempts:

            self.blocked_until = time.time() + self.block_time
            self.attempts = 0

            log_activite(
                message="Blocage 30s après 3 tentatives",
                module="security",
                utilisateur=username
            )

            QMessageBox.warning(
                self,
                "Bloqué",
                "Trop de tentatives. Attends 30 secondes."
            )

    # ───────── CLEAR ─────────
    def clear_fields(self):
        self.username.clear()
        self.password.clear()

    # ───────── PASSWORD TOGGLE ─────────
    def toggle_password(self):
        if self.btn_eye.isChecked():
            self.password.setEchoMode(QLineEdit.Normal)
            self.btn_eye.setIcon(QIcon("./resources/icons/hide.png"))
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.btn_eye.setIcon(QIcon("./resources/icons/visible.png"))

    # ───────── SIGNUP ─────────
    def signup(self):
        self.pageSignup = PageSignUp()
        self.pageSignup.show()
        self.close()

    # ───────── REDIRECTION ─────────
    def open_accueil(self):
        from modules.accueil import App
        from modules.employe.controller import EmployeController

        controller = EmployeController()
        self.window = App(controller)
        self.window.show()
        self.close()

    # ───────── DRAG WINDOW ─────────
    def mousePressEvent(self, event):
        self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
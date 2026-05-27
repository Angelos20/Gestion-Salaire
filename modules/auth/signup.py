from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QFrame, QHBoxLayout, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from configuration.database import get_connection
from configuration.security import hash_password
from resources.style import getStyleSheet
from modules.dashboard.controller import log_activite

# ─── Palette ─────────────────────────────
BG_DARK      = "#FFFFFF"
ACCENT       = "#0A1628"
WHITE        = "#0A1628"

class PageSignUp(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(getStyleSheet())
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.old_pos = None

        # ─── Layout principal ─────────────────
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # ─── Carte ──────────────────────────
        self.card = QFrame()
        self.card.setFixedWidth(460)
        self.card.setStyleSheet("""
            QFrame{
                background-color: white;
                border-radius: 20px;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(10)

        # CLOSE BUTTON
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.clicked.connect(self.close)
        self.btn_close.setObjectName("btn_close")
        top_layout.addWidget(self.btn_close)

        # TITLE
        self.titre = QLabel("Inscription")
        self.titre.setAlignment(Qt.AlignCenter)
        self.titre.setObjectName("titre")

        # NOM
        self.nom = QLineEdit()
        self.nom.setPlaceholderText("Nom complet")

        # USERNAME
        self.username = QLineEdit()
        self.username.setPlaceholderText("Nom d'utilisateur")

        # EMAIL
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        # password
        mdp_layout = QHBoxLayout()
        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)

        # Confirmation password
        self.conf_password = QLineEdit()
        self.conf_password.setPlaceholderText("Confirmer le mot de passe")
        self.conf_password.setEchoMode(QLineEdit.Password)

        self.btn_eye = QPushButton()
        self.btn_eye.setIcon(QIcon("./resources/icons/visible.png"))
        self.btn_eye.setIconSize(QSize(40, 40))
        self.btn_eye.setCheckable(True)
        self.btn_eye.clicked.connect(self.toggle_password)
        self.btn_eye.setStyleSheet("background: transparent; border: none;")

        mdp_layout.addWidget(self.password)
        mdp_layout.addWidget(self.btn_eye)


        # POSTE COMBOBOX
        self.poste = QComboBox()
        self.poste.addItems(["Directeur", "Manager", "Employé", "Comptable", "RH", "Administrateur"])

        # BUTTONS
        btn_layout = QHBoxLayout()
        self.btn_signup = QPushButton("S'inscrire")
        self.btn_cancel = QPushButton("Annuler")
        btn_layout.addWidget(self.btn_signup)
        btn_layout.addWidget(self.btn_cancel)

        # MESSAGE
        self.message = QLabel("")
        self.message.setAlignment(Qt.AlignCenter)

        # ASSEMBLAGE
        card_layout.addLayout(top_layout)
        card_layout.addWidget(self.titre)
        card_layout.addWidget(self.nom)
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.email)
        card_layout.addLayout(mdp_layout)
        card_layout.addWidget(self.conf_password)
        card_layout.addWidget(self.poste)
        card_layout.addLayout(btn_layout)
        card_layout.addWidget(self.message)
        self.card.setLayout(card_layout)
        main_layout.addWidget(self.card)
        self.setLayout(main_layout)

        # ACTIONS
        self.btn_signup.clicked.connect(self.signup_action)
        self.btn_cancel.clicked.connect(self.clear_fields)

    # ─── SIGNUP ACTION ─────────────────────
    def signup_action(self):
        nom = self.nom.text().strip()
        username = self.username.text().strip()
        email = self.email.text().strip()
        password = self.password.text().strip()
        confirm_password = self.conf_password.text().strip()
        poste = self.poste.currentText()

        if not all([nom, username, email, password]):

            msg = QMessageBox()
            msg.setWindowTitle("Erreur")
            msg.setText(f"Veuillez remplir tous les champs !")
            msg.setStyleSheet(self.styled_messagebox())
            msg.exec()

            return
        if password != confirm_password:

            msg = QMessageBox()
            msg.setWindowTitle("Erreur")
            msg.setText("Les mots de passe ne sont pas identiques !")
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(self.styled_messagebox())
            msg.exec()

            return

        hashed_password = hash_password(password)  # ✅ Hash une seule fois ici

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO utilisateur (nom, username, email, password, poste)
                VALUES (?, ?, ?, ?, ?)
            """, (nom, username, email, hashed_password, poste))
            conn.commit()
            conn.close()

            log_activite(
                f"Inscription réussie",
                module="auth-Inscription",
                utilisateur=username
            )

            msg = QMessageBox(self)
            msg.setWindowTitle("Succès")
            msg.setText(f"Utilisateur '{username}' créé avec succès !")
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet(self.styled_messagebox())
            msg.exec()

            from modules.auth.login import PageLogin
            self.login = PageLogin()
            self.login.show()
            self.close()

        except Exception as e:

            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText(f"Impossible de créer l'utilisateur.\n{str(e)}")
            msg.setIcon(QMessageBox.Critical)
            msg.setStyleSheet(self.styled_messagebox())
            msg.exec()
            print("Erreur signup:", e)

    # ───────── PASSWORD TOGGLE ─────────
    def toggle_password(self):
        if self.btn_eye.isChecked():
            self.password.setEchoMode(QLineEdit.Normal)
            self.conf_password.setEchoMode(QLineEdit.Normal)
            self.btn_eye.setIcon(QIcon("./resources/icons/hide.png"))
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.conf_password.setEchoMode(QLineEdit.Password)
            self.btn_eye.setIcon(QIcon("./resources/icons/visible.png"))

    # ─── CLEAR FIELDS ─────────────────────
    def clear_fields(self):
        self.nom.clear()
        self.username.clear()
        self.email.clear()
        self.password.clear()
        self.conf_password.clear()
        self.poste.setCurrentIndex(0)
        self.message.setText("")

    # ─── DRAG WINDOW ──────────────────────
    def mousePressEvent(self, event):
        self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

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
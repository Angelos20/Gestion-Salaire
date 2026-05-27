from PySide6.QtWidgets import (
    QApplication, QWidget, QFrame, QLabel, QVBoxLayout,QMainWindow,
    QHBoxLayout, QStackedWidget, QPushButton, QLineEdit,QMessageBox,
    QCheckBox, QTimeEdit, QFormLayout, QDoubleSpinBox, QTabWidget, QFileDialog
)
from PySide6.QtCore import Qt, QPoint, QSize, QTime
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QCursor, QPainterPath, QPixmap
)
import os
import sys
from modules.dashboard.ui import DashboardPage
from modules.employe.controller import EmployeController
from modules.salaire.ui import CalculSalaireView
from modules.presence.ui import PresenceUI
from modules.employe.ui import EmployeListe
from configuration.database import get_config, update_config
from modules.dashboard.controller import log_activite
from modules.parametre import ConfigRHView


# ─── Palette ─────────────────────────────────────────────────────────────────
BG_DARK      = "#FFFFFF"
BG_SIDEBAR   = "#0A1628"
BG_CARD      = "#EDF3FB"
ACCENT       = "#0A1628"
ACCENT_LIGHT = "#1E6FD9"
ACCENT_GLOW  = "#2A85FF"
WHITE        = "#0A1628"
GREY_LIGHT   = "#2C4A6E"
GREY_DIM     = "#5A7A9A"
DANGER       = "#C0392B"
SUCCESS      = "#1A8A4A"
BORDER       = "#C2D4E8"
SB_TEXT      = "#FFFFFF"
SB_SUBTEXT   = "#A8C0D6"
SB_DIM       = "#4A6080"

# ─── Symboles ─────────────────────────────────────────────────────────────────
ICON_DASHBOARD = "\u25A6"
ICON_EMPLOYES  = "\u2605"
ICON_SALAIRES  = "\u00A4"
ICON_PRESENCES = "\u25A1"
ICON_SETTINGS  = "\u2699"
ICON_QUIT      = "\u2715"
ICON_CLOSE     = "\u2715"
ICON_GENERAL   = "\u2302"
ICON_SECURITY  = "\u26BF"
ICON_PRINT     = "\u2399"
ICON_NETWORK   = "\u2316"
ICON_WARN      = "\u26A0"
ICON_MAIL      = "\u2709"
ICON_REPORT    = "\u25A6"
ICON_CHECK     = "\u2714"
ICON_MONEY     = "\u00A4"
ICON_CIRCLE    = "\u25CB"
ICON_EDIT      = "\u270E"


def qc(hex_color):
    """Convertit une couleur hex en QColor."""
    return QColor(hex_color)


def make_font(size=10, bold=False, family="Segoe UI"):
    f = QFont(family, size)
    if bold:
        f.setBold(True)
    return f


# ─── Bouton arrondi (Canvas → QWidget avec paintEvent) ───────────────────────
class RoundedButton(QWidget):
    def __init__(self, parent=None, text="", icon="", command=None,
                 width=180, height=48, radius=12,
                 bg=BG_CARD, fg=SB_TEXT, hover_bg=ACCENT_LIGHT,
                 active=False, on_sidebar=False):
        super().__init__(parent)
        self.btn_text    = text
        self.btn_icon    = icon
        self.command     = command
        self.radius      = radius
        self.bg_def      = hover_bg if active else ACCENT
        self.bg_hover    = bg
        self.fg          = fg
        self.active      = active
        self.on_sidebar  = on_sidebar
        self._hovered    = False
        self._current_bg = self.bg_def
        self.setFixedSize(width, height)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def set_active(self, active):
        self.active = active

        # ACTIVE = ancienne couleur hover
        if active:
            self.bg_def = ACCENT_LIGHT

        # INACTIVE = ancienne couleur normale
        else:
            self.bg_def = "#0D1F3C" if self.on_sidebar else BG_CARD

        self._current_bg = self.bg_def
        self.update()

    def enterEvent(self, event):
        self._hovered = True

        # HOVER = ancienne couleur inactive
        self._current_bg = "#0D1F3C" if self.on_sidebar else BG_CARD

        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self._current_bg = self.bg_def
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.command:
            self.command()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        r = self.radius

        # Ombre portée
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(3, 3, w - 4, h - 4, r, r)
        p.fillPath(shadow_path, qc(BORDER))

        # Corps principal
        body_path = QPainterPath()
        body_path.addRoundedRect(0, 0, w - 4, h - 4, r, r)
        p.fillPath(body_path, qc(self._current_bg))

        # Bordure
        border_color = qc(ACCENT_GLOW if self.active else BORDER)
        pen = QPen(border_color, 1)
        p.setPen(pen)
        p.drawPath(body_path)

        # Barre indicateur actif
        if self.active:
            bar_path = QPainterPath()
            bar_path.addRoundedRect(0, 8, 6, h - 20, 3, 3)
            p.fillPath(bar_path, qc(ACCENT_GLOW))

        # Texte
        txt_col = qc("#FFFFFF") if self.on_sidebar else qc(self.fg)
        p.setPen(QPen(txt_col))

        cx = (w - 4) // 2
        cy = (h - 4) // 2

        if self.btn_icon:
            # Icône centrée
            p.setFont(QFont("Segoe UI Symbol", 14, QFont.Bold))
            p.drawText(0, 0, w, h // 2,
                       Qt.AlignCenter, self.btn_icon)

            # Texte centré en dessous
            p.setFont(QFont("Segoe UI", 15, QFont.Bold))
            p.drawText(0, h // 2, w, h // 2,
                       Qt.AlignCenter, self.btn_text)
        else:
            p.setFont(QFont("Segoe UI", 15, QFont.Bold))
            p.drawText(0, 0, w - 4, h - 4,
                       Qt.AlignCenter, self.btn_text)
        p.end()


# ─── Logo Canvas ──────────────────────────────────────────────────────────────
class LogoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(62, 62)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(qc("#FFFFFF"))
        p.setPen(Qt.NoPen)
        p.drawEllipse(4, 4, 54, 54)
        p.setBrush(qc(ACCENT_LIGHT))
        p.drawEllipse(8, 8, 46, 46)
        p.setBrush(qc(BG_SIDEBAR))
        p.drawEllipse(16, 16, 30, 30)
        p.setPen(QPen(qc("#FFFFFF")))
        p.setFont(QFont("Segoe UI", 8, QFont.Bold))
        p.drawText(16, 16, 30, 30, Qt.AlignCenter, "GRH")
        p.end()


# ─── Widget séparateur horizontal ─────────────────────────────────────────────
def make_hsep(parent=None, color=BORDER):
    line = QFrame(parent)
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"background-color: {color}; border: none; max-height: 1px;")
    return line


def make_vsep(parent=None, color=BORDER):
    line = QFrame(parent)
    line.setFrameShape(QFrame.VLine)
    line.setStyleSheet(f"background-color: {color}; border: none; max-width: 1px;")
    return line


def make_label(text, font_size=10, bold=False, color=WHITE,
               bg=BG_DARK, wrap=0, align=Qt.AlignLeft):
    lbl = QLabel(text)
    lbl.setFont(make_font(font_size, bold))
    lbl.setStyleSheet(f"color: {color}; background: transparent;")
    if wrap:
        lbl.setWordWrap(True)
    lbl.setAlignment(align)
    return lbl


# ─── Carte KPI ────────────────────────────────────────────────────────────────
class KpiCard(QFrame):
    def __init__(self, sym, label, value, color=ACCENT, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        # Bande couleur en haut
        band = QFrame()
        band.setFixedHeight(3)
        band.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
        layout.addWidget(band)

        sym_lbl = QLabel(sym)
        sym_lbl.setFont(QFont("Segoe UI Symbol", 14, QFont.Bold))
        sym_lbl.setStyleSheet(f"color: {color}; background: transparent;")
        layout.addWidget(sym_lbl)

        val_lbl = QLabel(value)
        val_lbl.setFont(QFont("Segoe UI", 22, QFont.Bold))
        val_lbl.setStyleSheet(f"color: {WHITE}; background: transparent;")
        layout.addWidget(val_lbl)

        lbl_lbl = QLabel(label)
        lbl_lbl.setFont(make_font(9))
        lbl_lbl.setStyleSheet(f"color: {GREY_LIGHT}; background: transparent;")
        layout.addWidget(lbl_lbl)


# ══════════════════════════════════════════════════════════════════════════════
# APPLICATION PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════
class App(QMainWindow):
    def __init__(self, controller: EmployeController):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Gestion Salaire")
        self.showMaximized()
        self.setStyleSheet(f"QWidget {{ background-color: {BG_DARK}; }}")
        self._drag_pos = None
        self._nav_buttons = {}
        self._current_page = "dashboard"
        self._build_ui()
        log_activite(
            "Application ouverte",
            module="app",
            utilisateur="system"
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        main = self._build_main()
        root_layout.addWidget(main, 1)

    def make_round_pixmap(self, image_path, size=80):

        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            return QPixmap()

        # Redimensionnement
        pixmap = pixmap.scaled(
            size,
            size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        # Pixmap transparent final
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

    # ══════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ══════════════════════════════════════════════════════════════════════
    def _build_sidebar(self):

        config = get_config()

        nom_entreprise = "Entreprise"
        logo_path = ""

        try:
            nom_entreprise = config["nom_entreprise"] or "Entreprise"
            logo_path = config["logo_path"] or ""
        except:
            nom_entreprise = "Entreprise"
            logo_path = ""

        sb = QFrame()
        sb.setFixedWidth(250)

        sb.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SIDEBAR};
            }}

            QPushButton {{
                background-color: #0D1F3C;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
                font-family: Segoe UI;
            }}

            QPushButton:hover {{
                background-color: {ACCENT_LIGHT};
            }}

            QPushButton:checked {{
                background-color: {ACCENT_LIGHT};
                border-left: 4px solid #2A85FF;
            }}
        """)

        layout = QVBoxLayout(sb)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # ─────────────────────────
        # LOGO
        # ─────────────────────────
        self.logo_label = QLabel()

        self.logo_label.setFixedSize(90, 90)
        self.logo_label.setAlignment(Qt.AlignCenter)

        self.logo_label.setStyleSheet("""
            QLabel{
                background-color: white;
                border-radius: 45px;
                border: 3px solid #1E6FD9;
                padding: 2px;
            }
        """)

        if logo_path and os.path.exists(logo_path):
            pix = self.make_round_pixmap(logo_path, 80)
            self.logo_label.setPixmap(pix)

        layout.addWidget(self.logo_label, 0, Qt.AlignCenter)

        # ─────────────────────────
        # NOM ENTREPRISE
        # ─────────────────────────
        self.title_lbl = QLabel(nom_entreprise)
        self.title_lbl.setFont(QFont("Calibri", 16, QFont.Bold))

        self.title_lbl.setStyleSheet("""
            color: white;
            background: transparent;
        """)

        self.title_lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.title_lbl)

        # Sous titre
        sub_lbl = QLabel("Gestion des salaires")

        sub_lbl.setStyleSheet("""
            color: #A8C0D6;
            background: transparent;
            font-size: 11px;
        """)

        sub_lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(sub_lbl)

        layout.addSpacing(20)

        # ─────────────────────────
        # MENU
        # ─────────────────────────
        self.btn_dashboard = QPushButton(f"{ICON_DASHBOARD}  Dashboard")
        self.btn_employes = QPushButton(f"{ICON_EMPLOYES}  Employés")
        self.btn_salaires = QPushButton(f"{ICON_SALAIRES}  Salaires")
        self.btn_presences = QPushButton(f"{ICON_PRESENCES}  Présences")

        for btn in [
            self.btn_dashboard,
            self.btn_employes,
            self.btn_salaires,
            self.btn_presences
        ]:
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(48)

        self.btn_dashboard.setChecked(True)

        self.btn_dashboard.clicked.connect(
            lambda: self._navigate("dashboard"),
            self.refresh_sidebar()
        )

        self.btn_employes.clicked.connect(
            lambda: self._navigate("employes"),
            self.refresh_sidebar()
        )

        self.btn_salaires.clicked.connect(
            lambda: self._navigate("salaires"),
            self.refresh_sidebar()
        )

        self.btn_presences.clicked.connect(
            lambda: self._navigate("presences"),
            self.refresh_sidebar()
        )

        layout.addWidget(self.btn_dashboard)
        layout.addWidget(self.btn_employes)
        layout.addWidget(self.btn_salaires)
        layout.addWidget(self.btn_presences)

        layout.addStretch()

        # ─────────────────────────
        # BOTTOM BUTTONS
        # ─────────────────────────
        btn_settings = QPushButton(f"{ICON_SETTINGS}  Paramètres")

        btn_settings.clicked.connect(self._open_settings)

        btn_quit = QPushButton(f"{ICON_QUIT}  Quitter")

        btn_quit.setStyleSheet("""
            QPushButton{
                background-color: #3A0A0A;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-weight: bold;
            }

            QPushButton:hover{
                background-color: #C0392B;
            }
        """)

        btn_quit.clicked.connect(self._confirm_quit)

        layout.addWidget(btn_settings)
        layout.addWidget(btn_quit)

        # Version
        version = QLabel("v1.0.0 - 2026")

        version.setStyleSheet("""
            color: #4A6080;
            background: transparent;
            font-size: 10px;
        """)

        version.setAlignment(Qt.AlignCenter)

        layout.addWidget(version)

        return sb

    def _confirm_quit(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmation")
        msg.setText("Voulez-vous vraiment quitter l'application ?")

        msg.setIcon(QMessageBox.Warning)

        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        msg.setStyleSheet("""
                QMessageBox {
                    background-color: #F6F8FB;
                    color: #0A1640;
                    font-size: 13px;
                }

                QLabel {
                    color: #0A1640;
                    font-weight: bold;
                }

                QPushButton {
                    background-color: #0A1640;
                    color: white;
                    border-radius: 6px;
                    padding: 6px 14px;
                    font-weight: bold;
                }

                QPushButton:hover {
                    background-color: #1E6FD9;
                }

                QPushButton:pressed {
                    background-color: #163F7A;
                }
            """)

        result = msg.exec()

        if result == QMessageBox.Yes:
            self.close()

    def refresh_sidebar(self):

        config = get_config()

        try:
            nom_entreprise = config["nom_entreprise"] or "Entreprise"
            logo_path = config["logo_path"] or ""

        except:
            nom_entreprise = "Entreprise"
            logo_path = ""

        # nom
        self.title_lbl.setText(nom_entreprise)

        # logo
        if logo_path and os.path.exists(logo_path):

            pix = self.make_round_pixmap(logo_path, 80)

            self.logo_label.setPixmap(pix)

        else:
            self.logo_label.clear()
    # ══════════════════════════════════════════════════════════════════════
    # ZONE PRINCIPALE
    # ══════════════════════════════════════════════════════════════════════
    def _build_main(self):
        main = QWidget()
        main.setStyleSheet(f"QWidget {{ background-color: {BG_DARK}; }}")
        layout = QVBoxLayout(main)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Topbar
        topbar = QFrame()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet(f"QFrame {{ background-color: {BG_DARK}; }}")
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(24, 0, 8, 0)

        self._page_title_lbl = QLabel("Dashboard")
        self._page_title_lbl.setFont(QFont("Calibri", 20, QFont.Bold))
        self._page_title_lbl.setStyleSheet(f"color: {WHITE}; background: transparent;")
        tb_layout.addWidget(self._page_title_lbl)

        layout.addWidget(topbar)
        layout.addWidget(make_hsep(color=BORDER))

        # ── Stacked pages
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"QWidget {{ background-color: #1E6FD9; }}")
        layout.addWidget(self._stack, 1)

        self._pages = {}
        for key, builder in [
            ("dashboard", self._page_dashboard),
            ("employes",  self._page_employes),
            ("salaires",  self._page_salaires),
            ("presences", self._page_presences),
        ]:
            container = QWidget()
            container.setStyleSheet(f"background-color: {BG_DARK};")
            page_layout = QVBoxLayout(container)
            page_layout.setContentsMargins(24, 16, 24, 16)
            builder(page_layout)
            self._stack.addWidget(container)
            self._pages[key] = container

        self._navigate("dashboard")
        return main

    def _navigate(self, key):
        labels = {"dashboard": "Dashboard", "employes": "Employes",
                  "salaires":  "Salaires",  "presences": "Presences"}
        self._current_page = key
        self._page_title_lbl.setText(labels.get(key, key))
        for k, btn in self._nav_buttons.items():
            btn.set_active(k == key)

        self.btn_dashboard.setChecked(False)
        self.btn_employes.setChecked(False)
        self.btn_salaires.setChecked(False)
        self.btn_presences.setChecked(False)

        if key == "dashboard":
            self.btn_dashboard.setChecked(True)

        elif key == "employes":
            self.btn_employes.setChecked(True)

        elif key == "salaires":
            self.btn_salaires.setChecked(True)

        elif key == "presences":
            self.btn_presences.setChecked(True)

        self._stack.setCurrentWidget(self._pages[key])

        log_activite(
            f"Navigation vers {key}",
            module="ui",
            utilisateur="system"
        )
    # ══════════════════════════════════════════════════════════════════════
    # PAGE DASHBOARD  — vide (comme employes)
    # ══════════════════════════════════════════════════════════════════════
    def _page_dashboard(self, layout):
        dashboard_widget = DashboardPage()
        layout.addWidget(dashboard_widget)

    def _page_employes(self, layout):
        employes_widget = EmployeListe(self.controller)
        layout.addWidget(employes_widget)

    def _page_salaires(self, layout):
        salaire_widget = CalculSalaireView()
        layout.addWidget(salaire_widget)

    def _page_presences(self, layout):
        presence_widget = PresenceUI()
        layout.addWidget(presence_widget)

    # ══════════════════════════════════════════════════════════════════════
    # PARAMETRES
    # ══════════════════════════════════════════════════════════════════════
    def _open_settings(self):
        log_activite(
            "Ouverture paramètres",
            module="ui",
            utilisateur="system"
        )
        self._settings_win = ConfigRHView()
        self._settings_win.move(self.x() + 180, self.y() + 90)
        self._settings_win.show()

        self._settings_win.destroyed.connect(
            self.refresh_sidebar
        )

    def closeEvent(self, event):
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmation")
        msg.setText("Voulez-vous vraiment quitter l'application ?")

        msg.setIcon(QMessageBox.Warning)

        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        msg.setStyleSheet("""
                QMessageBox {
                    background-color: #F6F8FB;
                    color: #0A1640;
                    font-size: 13px;
                }

                QLabel {
                    color: #0A1640;
                    font-weight: bold;
                }

                QPushButton {
                    background-color: #0A1640;
                    color: white;
                    border-radius: 6px;
                    padding: 6px 14px;
                    font-weight: bold;
                }

                QPushButton:hover {
                    background-color: #1E6FD9;
                }

                QPushButton:pressed {
                    background-color: #163F7A;
                }
            """)

        result = msg.exec()

        if result == QMessageBox.Yes:
            self.close()
# ─── Widget cercle icone ──────────────────────────────────────────────────────
class _IconCircle(QWidget):
    def __init__(self, sym, parent=None):
        super().__init__(parent)
        self.sym = sym
        self.setFixedSize(90, 90)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(qc(BG_CARD))
        pen = QPen(qc(ACCENT_LIGHT), 2)
        p.setPen(pen)
        p.drawEllipse(5, 5, 80, 80)
        p.setPen(QPen(qc(ACCENT)))
        p.setFont(QFont("Segoe UI Symbol", 28, QFont.Bold))
        p.drawText(5, 5, 80, 80, Qt.AlignCenter, self.sym)
        p.end()


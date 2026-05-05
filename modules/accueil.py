from PySide6.QtWidgets import (
    QApplication, QWidget, QFrame, QLabel, QVBoxLayout,
    QHBoxLayout, QStackedWidget, QPushButton, QLineEdit,QMessageBox,
    QCheckBox, QTimeEdit, QFormLayout, QDoubleSpinBox, QTabWidget, QFileDialog
)
from PySide6.QtCore import Qt, QPoint, QSize, QTime
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QCursor, QPainterPath, QPixmap
)
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
        self.bg_def      = ACCENT if active else bg
        self.bg_hover    = hover_bg
        self.fg          = fg
        self.active      = active
        self.on_sidebar  = on_sidebar
        self._hovered    = False
        self._current_bg = self.bg_def
        self.setFixedSize(width, height)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def set_active(self, active):
        self.active = active
        self.bg_def = ACCENT if active else ("#0D1F3C" if self.on_sidebar else BG_CARD)
        self._current_bg = self.bg_def
        self.update()

    def enterEvent(self, event):
        self._hovered = True
        self._current_bg = self.bg_hover
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
            # Icone
            p.setFont(QFont("Segoe UI Symbol", 11, QFont.Bold))
            p.drawText(cx - 55, 0, 40, h - 4,
                       Qt.AlignCenter, self.btn_icon)
            # Texte
            p.setFont(QFont("Segoe UI", 10, QFont.Bold))
            p.drawText(cx - 10, 0, 80, h - 4,
                       Qt.AlignCenter, self.btn_text)
        else:
            p.setFont(QFont("Segoe UI", 10, QFont.Bold))
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
class App(QWidget):
    def __init__(self, controller: EmployeController):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("GRH Pro")
        self.setFixedSize(1850, 950)
        self.setStyleSheet(f"QWidget {{ background-color: {BG_DARK}; }}")
        self._drag_pos = None
        self._center()
        self._nav_buttons = {}
        self._current_page = "dashboard"
        self._build_ui()
        log_activite(
            "Application ouverte",
            module="app",
            utilisateur="system"
        )

    def _center(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width()  - 1850) // 2
        y = (screen.height() - 950)  // 2
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def _build_ui(self):
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        main = self._build_main()
        root_layout.addWidget(main, 1)

    # ══════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ══════════════════════════════════════════════════════════════════════
    def _build_sidebar(self):
        sb = QFrame()
        sb.setFixedWidth(240)
        sb.setStyleSheet(f"QFrame {{ background-color: {BG_SIDEBAR}; }}")
        layout = QVBoxLayout(sb)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header / Logo
        header = QWidget()
        header.setStyleSheet(f"background-color: {BG_SIDEBAR};")
        h_layout = QVBoxLayout(header)
        h_layout.setAlignment(Qt.AlignCenter)
        h_layout.setContentsMargins(0, 20, 0, 10)

        logo = LogoWidget()
        h_layout.addWidget(logo, 0, Qt.AlignCenter)

        title_lbl = QLabel("G.S")
        title_lbl.setFont(QFont("Calibri", 15, QFont.Bold))
        title_lbl.setStyleSheet(f"color: {SB_TEXT}; background: transparent;")
        title_lbl.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(title_lbl)

        sub_lbl = QLabel("Gestion des salaires")
        sub_lbl.setFont(make_font(9))
        sub_lbl.setStyleSheet(f"color: {SB_SUBTEXT}; background: transparent;")
        sub_lbl.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(sub_lbl)

        layout.addWidget(header)
        layout.addWidget(make_hsep(color="#1E3A5F"))

        nav_items = [
            (ICON_DASHBOARD, "Dashboard",  "dashboard"),
            (ICON_EMPLOYES,  "Employes",   "employes"),
            (ICON_SALAIRES,  "Salaires",   "salaires"),
            (ICON_PRESENCES, "Presences",  "presences"),
        ]
        for icon, label, key in nav_items:
            active = (key == self._current_page)
            btn = RoundedButton(sb, text=label, icon=icon,
                                width=208, height=46, radius=10,
                                bg="#0D1F3C",
                                hover_bg=ACCENT_LIGHT,
                                active=active,
                                on_sidebar=True,
                                command=lambda k=key: self._navigate(k))
            wrapper = QWidget()
            wrapper.setStyleSheet(f"background: transparent;")
            wl = QHBoxLayout(wrapper)
            wl.setContentsMargins(16, 3, 16, 3)
            wl.addWidget(btn)
            layout.addWidget(wrapper)
            self._nav_buttons[key] = btn

        layout.addWidget(make_hsep(color="#1E3A5F"))
        layout.addStretch()

        bottom_items = [
            (ICON_SETTINGS, "Parametres", "#0D1F3C", ACCENT_LIGHT, self._open_settings),
            (ICON_QUIT,     "Quitter",    "#3A0A0A", "#C0392B",    self.close),
        ]
        for icon, label, col, hover, cmd in bottom_items:
            btn = RoundedButton(sb, text=label, icon=icon,
                                width=208, height=46, radius=10,
                                bg=col, hover_bg=hover,
                                on_sidebar=True,
                                command=cmd)
            wrapper = QWidget()
            wrapper.setStyleSheet("background: transparent;")
            wl = QHBoxLayout(wrapper)
            wl.setContentsMargins(16, 3, 16, 3)
            wl.addWidget(btn)
            layout.addWidget(wrapper)

        #layout.addStretch()

        version = QLabel("v1.0.0  -  2025")
        version.setFont(make_font(9))
        version.setStyleSheet(f"color: {SB_DIM}; background: transparent;")
        version.setAlignment(Qt.AlignCenter)
        version.setContentsMargins(0, 0, 0, 12)
        layout.addWidget(version)

        return sb

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
        self._stack.setStyleSheet(f"QWidget {{ background-color: {BG_DARK}; }}")
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


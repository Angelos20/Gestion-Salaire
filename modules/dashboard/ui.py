from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QFrame, QGraphicsDropShadowEffect,
    QScrollArea, QDateEdit, QPushButton
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QDate, Signal
from PySide6.QtGui import QFont, QPixmap
from datetime import datetime

from modules.dashboard.controller import get_kpis, get_alertes, get_recent_activities
from modules.dashboard.charts import ChartCanvas
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def load_icon(path, size=42):
    pixmap = QPixmap(path)

    if pixmap.isNull():
        print("❌ Image introuvable :", path)

    return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

# ================= LABEL CLIQUABLE =================
class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


# ================= CARTE ANIMÉE =================
class AnimatedCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setYOffset(2)
        self.setGraphicsEffect(self.shadow)

        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)


# ================= DASHBOARD =================
class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        self.last_activities = []

        self.setStyleSheet("""
        QWidget {
            background-color: #F4F6F9;
            font-family: Segoe UI;
        }
        QLabel {
            color: #111827;
        }
        """)

        main_layout = QVBoxLayout(self)

        # ================= HEADER =================
        header = QHBoxLayout()

        self.btn_actualiser = QPushButton("Actualiser")
        self.btn_actualiser.clicked.connect(self.rafraichir)
        self.btn_actualiser.setStyleSheet("""
            QPushButton {
                background-color: #0A1640;
                color: white;
                font-weight: bold;
                font-size: 15px;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color:#1E6FD9; }
        """)

        self.date_fin = QDateEdit()
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_fin.setDate(QDate.currentDate())
        self.date_fin.setCalendarPopup(True)
        self.date_fin.dateChanged.connect(self.update_selected_date)

        self.selected_date = self.date_fin.date().toString("yyyy-MM-dd")

        self.time_label = QLabel()

        header.addStretch()
        header.addWidget(self.btn_actualiser)
        header.addWidget(self.date_fin)
        header.addWidget(self.time_label)
        main_layout.addLayout(header)

        # ================= KPI =================
        self.grid = QGridLayout()
        self.kpi_labels = []

        kpi_data = [
            (str(BASE_DIR / "resources/icons/user.png"), "Total employés", "#3B82F6"),
            (str(BASE_DIR / "resources/icons/masse.png"), "Masse salariale", "#10B981"),
            (str(BASE_DIR / "resources/icons/moyenn.png"), "Salaire moyen", "#F59E0B"),
            (str(BASE_DIR / "resources/icons/paye.png"), "Total payé", "#EF4444"),
        ]

        for i, (icon, title, color) in enumerate(kpi_data):
            card = AnimatedCard()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border-radius: 12px;
                    border-left: 6px solid {color};
                }}
            """)

            layout = QVBoxLayout(card)

            # ================= ICON (PIXMAP STICKER) =================
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignCenter)

            icon_label.setPixmap(load_icon(icon, 48))  # ✅ ICI

            # ================= VALUE =================
            value = QLabel("0")
            value.setAlignment(Qt.AlignCenter)
            value.setFont(QFont("Segoe UI", 20, QFont.Bold))
            value.setStyleSheet(f"color: {color};")

            # ================= TITLE =================
            label = QLabel(title)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color:#374151;")

            layout.addWidget(icon_label)
            layout.addWidget(value)
            layout.addWidget(label)

            self.grid.addWidget(card, i // 4, i % 4)
            self.kpi_labels.append(value)

        main_layout.addLayout(self.grid)

        # ================= CHARTS =================
        self.chart1 = ChartCanvas()
        self.chart2 = ChartCanvas()
        self.chart3 = ChartCanvas()

        self.chart1.setFixedHeight(250)
        self.chart2.setFixedHeight(250)
        self.chart3.setFixedHeight(250)

        chart_layout = QHBoxLayout()
        chart_layout.addWidget(self.create_chart("Présence", self.chart1))
        chart_layout.addWidget(self.create_chart("Salaire", self.chart2))
        chart_layout.addWidget(self.create_chart("Répartition", self.chart3))
        main_layout.addLayout(chart_layout)

        # ================= ALERTES =================
        self.alert_container = QWidget()
        self.alert_layout = QVBoxLayout(self.alert_container)

        self.alert_scroll = QScrollArea()
        self.alert_scroll.setWidgetResizable(True)
        self.alert_scroll.setWidget(self.alert_container)
        self.alert_scroll.setMaximumHeight(140)

        main_layout.addWidget(self.wrap_card(self.alert_scroll))

        # ================= ACTIVITÉS =================
        self.activity_container = QWidget()
        self.activity_layout = QVBoxLayout(self.activity_container)

        self.activity_scroll = QScrollArea()
        self.activity_scroll.setWidgetResizable(True)
        self.activity_scroll.setWidget(self.activity_container)
        self.activity_scroll.setMaximumHeight(160)

        main_layout.addWidget(self.wrap_card(self.activity_scroll))

        # ================= TIMER =================
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(3000)

        self.update_data()

    # ================= UTILS =================
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def create_chart(self, title, chart):
        card = AnimatedCard()
        layout = QVBoxLayout(card)
        layout.addWidget(QLabel(title))
        layout.addWidget(chart)
        return card

    def wrap_card(self, widget):
        card = AnimatedCard()
        layout = QVBoxLayout(card)
        layout.addWidget(widget)
        return card

    # ================= TIME =================
    def update_time(self):
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))

    # ================= DATA =================
    def update_data(self):
        kpis = get_kpis(self.selected_date)

        values = [
            max(0, int(kpis.get("employes") or 0)),
            max(0, float(kpis.get("masse_salariale") or 0)),
            max(0, float(kpis.get("salaire_moyen") or 0)),
            max(0, float(kpis.get("total_paye") or 0))
        ]

        for label, val in zip(self.kpi_labels, values):
            if isinstance(val, float):
                label.setText(f"{val:,.2f}")
            else:
                label.setText(str(val))

        self.chart1.plot_presence(
            kpis.get("present") or 0,
            kpis.get("absent") or 0,
            kpis.get("retard") or 0,
            kpis.get("depart") or 0
        )

        self.chart2.plot_salary(
            kpis.get("masse_salariale") or 0,
            kpis.get("total_paye") or 0
        )

        self.chart3.plot_pie(
            kpis.get("present") or 0,
            kpis.get("absent") or 0,
            kpis.get("retard") or 0,
            kpis.get("depart") or 0
        )

        # ================= ALERTES =================
        self.clear_layout(self.alert_layout)

        title = QLabel("Notifications")
        title.setStyleSheet("font-weight:bold;font-size:14px;")
        self.alert_layout.addWidget(title)

        for a in get_alertes(self.selected_date):
            label = ClickableLabel(f"⚠ {a}")
            label.setCursor(Qt.PointingHandCursor)

            if "absent" in a.lower() or "retard" in a.lower():
                label.clicked.connect(self.open_presence_window)

            self.alert_layout.addWidget(label)

        # ================= ACTIVITÉS =================
        self.clear_layout(self.activity_layout)

        title2 = QLabel("Activités récentes")
        title2.setStyleSheet("font-weight:bold;font-size:14px;")
        self.activity_layout.addWidget(title2)

        activities = get_recent_activities(self.selected_date) or ["Aucune activité"]

        for a in activities:
            self.activity_layout.addWidget(QLabel(f"🔹 {a}"))

    # ================= REFRESH =================
    def refresh(self):
        if not self.isVisible():
            return

        self.update_data()

    # ================= PRESENCE WINDOW =================
    def open_presence_window(self):
        from modules.presence.liste_presence import ListePresence
        self.presence_window = ListePresence()
        self.presence_window.show()

    # ================= DATE =================
    def update_selected_date(self, qdate):
        self.selected_date = qdate.toString("yyyy-MM-dd")
        self.update_data()

    # ================= BUTTON =================
    def rafraichir(self):
        self.update_data()
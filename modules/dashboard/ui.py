from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QFrame, QGraphicsDropShadowEffect, QScrollArea, QDateEdit, QPushButton
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QDate
from PySide6.QtGui import QFont
from datetime import datetime

from modules.dashboard.controller import get_kpis, get_alertes, get_recent_activities
from modules.dashboard.charts import ChartCanvas


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
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(10)
        self.anim.setEndValue(25)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(25)
        self.anim.setEndValue(10)
        self.anim.start()
        super().leaveEvent(event)


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

        self.date_fin = QDateEdit()
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_fin.setStyleSheet("color:black;font-family: sans-serif;")
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
            ("👥", "Total employés"),
            ("💰", "Masse salariale"),
            ("📉", "Salaire moyen"),
            ("💵", "Total payé"),
        ]

        for i, (icon, title) in enumerate(kpi_data):
            card = AnimatedCard()
            layout = QVBoxLayout(card)

            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFont(QFont("Segoe UI Emoji", 42))
            icon_label.setStyleSheet("color: #2563EB; margin-bottom: 6px;")

            value = QLabel("0")
            value.setAlignment(Qt.AlignCenter)
            value.setFont(QFont("Segoe UI", 20, QFont.Bold))

            label = QLabel(title)
            label.setAlignment(Qt.AlignCenter)

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
        self.alert_scroll.setMaximumHeight(120)

        main_layout.addWidget(self.wrap_card(self.alert_scroll))

        # ================= ACTIVITÉS =================
        self.activity_container = QWidget()
        self.activity_layout = QVBoxLayout(self.activity_container)

        self.activity_scroll = QScrollArea()
        self.activity_scroll.setWidgetResizable(True)
        self.activity_scroll.setWidget(self.activity_container)
        self.activity_scroll.setMaximumHeight(150)

        main_layout.addWidget(self.wrap_card(self.activity_scroll))

        # ================= TIMER =================
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(3000)

        self.update_data()

    def rafraichir(self):
        self.refresh()
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
        date = self.selected_date
        kpis = get_kpis(date)

        values = [
            kpis.get("employes") or 0,
            kpis.get("masse_salariale") or 0,
            kpis.get("salaire_moyen") or 0,
            kpis.get("total_paye") or 0
        ]

        for label, val in zip(self.kpi_labels, values):
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

        pie_values = [
            kpis.get("present") or 0,
            kpis.get("absent") or 0,
            kpis.get("retard") or 0,
            kpis.get("depart") or 0
        ]

        if sum(pie_values) == 0:
            pie_values = [1, 1, 1, 1]

        self.chart3.plot_pie(*pie_values)

        # ================= ALERTES =================
        alertes = get_alertes(date) or ["Aucune alerte"]

        self.clear_layout(self.alert_layout)

        for a in alertes:
            self.alert_layout.addWidget(QLabel(f"⚠ {a}"))

        # ================= ACTIVITÉS =================
        activities = get_recent_activities(date)

        if not isinstance(activities, list):
            activities = activities[-30:]
        if not activities:
            activities = ["Aucune activité récente"]

        self.clear_layout(self.activity_layout)

        for a in activities:
            self.activity_layout.addWidget(QLabel(f"🔹 {a}"))

    # ================= REFRESH =================
    def refresh(self):
        if not self.isVisible():
            return

        activities = get_recent_activities(self.selected_date)

        if not isinstance(activities, list):
            return

        activities = list(map(str, activities))

        if hash(tuple(activities)) == getattr(self, "_activity_hash", None):
            return

        self.clear_layout(self.activity_layout)

        for a in activities:
            self.activity_layout.addWidget(QLabel(f"🔹 {a}"))

        self._activity_hash = hash(tuple(activities))

    # ================= DATE =================
    def update_selected_date(self, qdate):
        self.selected_date = qdate.toString("yyyy-MM-dd")
        self.update_data()
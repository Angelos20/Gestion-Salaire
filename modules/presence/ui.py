#ui presence
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QHeaderView, QTableWidget,
    QStackedWidget, QTableWidgetItem, QMessageBox,QAbstractItemView,QTimeEdit, QDialog
)
from PySide6.QtCore import Qt, QTime, QTimer
from datetime import datetime
from configuration.database import get_connection, get_config
from modules.presence.model import ajouter_presence
from modules.presence.liste_presence import ListePresence
from modules.dashboard.controller import log_activite
from configuration.security import get_user
from configuration.audit_model import AuditModel

class TimeDialog(QDialog):
    def __init__(self, title="Heure", default_time="08:15", parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setFixedSize(320, 180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.setStyleSheet(parent.dialogStyle()) #if parent else "")

        title_label = QLabel("⏰ " + title)
        title_label.setStyleSheet("font-size:16px; font-weight:bold; color:#0A1628;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        heures, minutes = map(int, default_time.split(":"))
        self.time_edit = QTimeEdit(QTime(heures, minutes))
        self.time_edit.setDisplayFormat("HH:mm")

        layout.addWidget(self.time_edit)

        btn_layout = QHBoxLayout()

        self.btn_cancel = QPushButton("Annuler")

        self.btn_cancel.clicked.connect(self.reject)

        self.btn_ok = QPushButton("Valider")
        self.btn_ok.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)

        layout.addLayout(btn_layout)

    def get_time(self):
        return self.time_edit.time().toString("HH:mm")

    def dialogStyle(self):
        return """
            QDialog {
                background-color: #EDF3FB;
                border-radius: 15px;
            }

            QLabel {
                color: #0A1628;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }

            QAbstractSpinBox {
                color: black;
                background-color: white;
            }

            QTimeEdit {
                background-color: white;
                border: 2px solid #1E6FD9;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
                font-weight: bold;

                color: black;
                selection-color: black;
                selection-background-color: #D6E8FF;
            }

            QTimeEdit:hover {
                border: 2px solid #2A85FF;
            }

            QTimeEdit:focus {
                border: 2px solid #2A85FF;
                background-color: #F4F8FF;
                color: black;
            }

            QPushButton {
                background-color: #0A1640;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 18px;
                border-radius: 8px;
                min-width: 100px;
            }

            QPushButton:hover {
                background-color: #1E6FD9;
            }
        """

class TableauPresenceView(QWidget):
    """Vue tableau de présence adaptée au style CalculSalaireView"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self.getStyleSheet())
        self.audit = AuditModel()
        self.setStyleSheet("background-color: #f8f9fa;")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Zone de recherche et bouton nouvelle présence ---
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(20, 20, 20, 20)
        search_layout.setSpacing(10)

        self.ent_search = QLineEdit()
        self.ent_search.setPlaceholderText("🔍 Rechercher un employé...")
        self.ent_search.setFixedWidth(500)
        self.ent_search.textChanged.connect(self.filter_table)
        self.ent_search.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #ddd;
                color: black;
                font-family: sans-serif;
            }
    
            QLineEdit:focus {
                border: 1px solid #1877f2;
            }
        """)
        search_layout.addWidget(self.ent_search)

        #Bouton nouvelle presence
        self.btn_reset = QPushButton("Nouvelle fiche")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.setStyleSheet(self.getStyleSheet())

        # Bouton fiche de presence
        self.btn_fiche = QPushButton("Liste de Présence")
        self.btn_fiche.setCursor(Qt.PointingHandCursor)
        self.btn_fiche.setStyleSheet(self.getStyleSheet())

        # Bouton fiche d"actualisation
        self.btn_actualiser = QPushButton("Actualiser")
        self.btn_actualiser.setCursor(Qt.PointingHandCursor)
        self.btn_actualiser.setStyleSheet(self.getStyleSheet())

        self.btn_fiche.clicked.connect(self.fiche)
        self.btn_reset.clicked.connect(self.nouvelle_fiche)
        self.btn_actualiser.clicked.connect(self.actualiser)
        search_layout.addStretch()
        search_layout.addWidget(self.btn_actualiser)
        search_layout.addWidget(self.btn_reset)
        search_layout.addWidget(self.btn_fiche)

        layout.addWidget(search_container)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Prénoms", "Poste", "Actions"])
        # Numéro de ligne (vertical header)
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setDefaultSectionSize(30)

        # Sélection par ligne entière
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Désactiver édition
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Supprimer focus (cadre au clic)
        self.table.setFocusPolicy(Qt.NoFocus)

        # Style
        self.table.setStyleSheet("""
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

        #self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        hdr = self.table.horizontalHeader()
        for i in range(4):
            hdr.setSectionResizeMode(i, QHeaderView.Stretch)

        table_wrap = QVBoxLayout()
        table_wrap.setContentsMargins(20, 0, 20, 20)
        table_wrap.addWidget(self.table)
        layout.addLayout(table_wrap)

        self.load_employes()

    def dialogStyle(self):
        return """
            QDialog {
                background-color: #F5F7FA;
                border-radius: 12px;
            }

            QLabel {
                color: #1A2C3E;
                font-size: 14px;
                font-family: sans-serif;
            }

            QPushButton {
                background-color: #0A1640;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: #1E6FD9;
            }

            QPushButton:pressed {
                background-color: #0A1628;
            }
        """


    def styled_message(self, title, text, icon="info"):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: #F5F7FA;
            }

            QLabel {
                color: #1A2C3E;
                font-size: 13px;
            }

            QPushButton {
                background-color: #0A1640;
                color: white;
                padding: 6px 14px;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1E6FD9;
            }
        """)

        if icon == "success":
            msg.setIcon(QMessageBox.Information)
        elif icon == "error":
            msg.setIcon(QMessageBox.Critical)
        elif icon == "warning":
            msg.setIcon(QMessageBox.Warning)
        else:
            msg.setIcon(QMessageBox.Information)

        return msg

    # ───────── LOGIQUE TABLEAU ─────────
    def filter_table(self):
        text = self.ent_search.text().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            nom = item.text().lower() if item else ""
            self.table.setRowHidden(row, text not in nom)

    def actualiser(self):
        self.load_employes()

    def load_employes(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, prenom, poste FROM employes")
        data = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            emp_id, nom, poste = row_data

            # ID
            item_id = QTableWidgetItem(str(emp_id))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, item_id)

            # Nom
            item_nom = QTableWidgetItem(nom)
            item_nom.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, item_nom)

            # Poste
            item_poste = QTableWidgetItem(poste)
            item_poste.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 2, item_poste)

            # Actions
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(2)

            btn_present = QPushButton("Présent")
            btn_absent = QPushButton("Absent")
            btn_retard = QPushButton("Retard")
            btn_depart = QPushButton("Partir tôt")

            # Styles avec boutons plus grands (40px de hauteur)
            for btn, color in zip(
                    [btn_present, btn_absent, btn_retard, btn_depart],
                    ["#4da6ff", "#6699cc", "#3399ff", "#1a66cc"]
            ):
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: white;
                        border-radius: 5px;
                        height: 40px;
                        font-weight: bold;
                        font-size: 11px;
                    }}
                    QPushButton:hover {{
                        background-color: #004c99;
                    }}
                """)

            # Connexions des boutons
            btn_present.clicked.connect(self.make_handler(emp_id, "present", action_layout))
            btn_absent.clicked.connect(self.make_handler(emp_id, "absent", action_layout))
            btn_retard.clicked.connect(self.make_handler(emp_id, "retard", action_layout))
            btn_depart.clicked.connect(self.make_handler(emp_id, "depart", action_layout))

            action_layout.addWidget(btn_present)
            action_layout.addWidget(btn_absent)
            action_layout.addWidget(btn_retard)
            action_layout.addWidget(btn_depart)
            action_widget.setLayout(action_layout)

            self.table.setCellWidget(row_idx, 3, action_widget)

        # Si aucune ligne, garder tableau visible avec un message vide
        if len(data) == 0:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("Aucun employé trouvé")
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.table.setSpan(0, 0, 1, 4)  # Occuper toutes les colonnes
            self.table.setItem(0, 0, empty_item)

    def disable_row_buttons(self, layout):
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setEnabled(False)
                widget.setStyleSheet("""
                    QPushButton {
                        background-color: #B0B0B0; /* gris */
                        color: #666666;
                        border-radius: 5px;
                        height: 40px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                """)

    def nouvelle_fiche(self):
        # réactiver tous les boutons de toutes les lignes
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 3)
            if widget:
                layout = widget.layout()
                for i in range(layout.count()):
                    btn = layout.itemAt(i).widget()
                    if isinstance(btn, QPushButton):
                        btn.setEnabled(True)

                        # restaurer style normal
                        if btn.text() == "Présent":
                            color = "#4da6ff"
                        elif btn.text() == "Absent":
                            color = "#6699cc"
                        elif btn.text() == "Retard":
                            color = "#3399ff"
                        elif btn.text() == "Partir tôt":
                            color = "#1a66cc"
                        else:
                            color = "#cccccc"

                        btn.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {color};
                                color: white;
                                border-radius: 5px;
                                height: 40px;
                                font-weight: bold;
                                font-size: 11px;
                            }}
                            QPushButton:hover {{
                                background-color: #004c99;
                            }}
                        """)

        self.styled_message("Succès", "Nouvelle fiche activée", "success").exec()


    def fiche(self):
        self.fiche_presence = ListePresence()
        self.fiche_presence.show()

    def make_handler(self, emp_id, statut, layout):
        return lambda: self.handle_action(emp_id, statut, None, layout)

    def handle_action(self, employe_id, statut, time_edit, layout):

        date = datetime.now().strftime("%Y-%m-%d")

        # ─────────────────────────────
        # CONFIGURATION
        # ─────────────────────────────
        config = get_config() or {}

        # valeurs par défaut si config est vide ou None
        heure_matin_debut = config.get("heure_matin_debut", "08:00")
        heure_matin_fin = config.get("heure_matin_fin", "12:00")

        heure_aprem_debut = config.get("heure_aprem_debut", "13:00")
        heure_aprem_fin = config.get("heure_aprem_fin", "17:00")

        # ─────────────────────────────
        # DEMANDE SESSION
        # ─────────────────────────────
        msg = QMessageBox(self)
        msg.setWindowTitle("Session de présence")
        msg.setText("Sélectionnez la session :")
        msg.setIcon(QMessageBox.Question)
        msg.setStyleSheet(self.getStyleSheet())
        btn_matin = msg.addButton("Matin", QMessageBox.YesRole)
        btn_apres_midi = msg.addButton("Après-midi", QMessageBox.NoRole)

        msg.exec()

        is_matin = (msg.clickedButton() == btn_matin)

        # heures selon session
        if is_matin:

            heure_debut = heure_matin_debut
            heure_fin = heure_matin_fin
            periode = "matin"

        else:

            heure_debut = heure_aprem_debut
            heure_fin = heure_aprem_fin
            periode = "apres_midi"

        heure_entree = None
        heure_sortie = None

        # ─────────────────────────────
        # PRÉSENT
        # ─────────────────────────────
        if statut == "present":

            heure_entree = heure_debut
            heure_sortie = heure_fin

        # ─────────────────────────────
        # ABSENT
        # ─────────────────────────────
        elif statut == "absent":

            heure_entree = None
            heure_sortie = None

        # ─────────────────────────────
        # RETARD
        # ─────────────────────────────
        elif statut == "retard":

            dialog = TimeDialog(
                f"Heure arrivée ({periode})",
                heure_debut,
                self
            )

            if dialog.exec():

                heure_entree = dialog.get_time()
                heure_sortie = heure_fin

            else:
                return

        # ─────────────────────────────
        # DÉPART TÔT
        # ─────────────────────────────
        elif statut == "depart":

            dialog = TimeDialog(
                f"Heure départ ({periode})",
                heure_fin,
                self
            )
            if dialog.exec():

                heure_sortie = dialog.get_time()
                heure_entree = heure_debut

            else:
                return

        # ─────────────────────────────
        # ENREGISTREMENT
        # ─────────────────────────────
        ajouter_presence(
            employe_id,
            date,
            heure_entree,
            heure_sortie,
            statut
        )

        user = get_user()

        log_activite(
            f"Ajout présence {statut} ({periode}) - employé {employe_id}",
            module="presence",
            utilisateur=user["username"]
        )

        self.audit.log(
            action="INSERT",
            table="presence",
            record_id=employe_id,
            old_data=None,
            new_data={
                "employe_id": employe_id,
                "date": date,
                "heure_entree": heure_entree,
                "heure_sortie": heure_sortie,
                "statut": statut,
                "periode": periode
            },
            utilisateur=user["username"]
        )

        # ─────────────────────────────
        # DÉSACTIVER BOUTONS
        # ─────────────────────────────
        for row in range(self.table.rowCount()):

            item = self.table.item(row, 0)

            if item and item.text() == str(employe_id):
                self.disable_row_buttons(
                    self.table.cellWidget(row, 3).layout()
                )

                break

    def getStyleSheet(self):
        return """
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

        QPushButton:checked {
            background-color: #0A1640;
        }

        QDialog {
            background-color: #EDF3FB;
            border-radius: 15px;
        }

        QLabel {
            color: #0A1628;
            font-size: 14px;
            font-weight: bold;
        }

        QTimeEdit {
            background-color: white;
            border: 2px solid #1E6FD9;
            border-radius: 8px;
            padding: 6px;
            font-size: 14px;
            color: black;
        }

        QTimeEdit:hover {
            border: 2px solid #2A85FF;
        }

        QTimeEdit:focus {
            border: 2px solid #2A85FF;
            background-color: #F4F8FF;
        }
        QMessageBox {
            background-color: #EDF3FB;
            font-size: 13px;
        }
        """
class PresenceUI(QWidget):
    """Interface principale avec header et stacked widget"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f8f9fa;")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Stack : tableau présence ──
        self.stack = QStackedWidget()
        self.vue_tableau = TableauPresenceView()
        self.stack.addWidget(self.vue_tableau)
        layout.addWidget(self.stack)
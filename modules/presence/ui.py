from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QHeaderView, QTableWidget,
    QStackedWidget, QTableWidgetItem, QMessageBox,QAbstractItemView,QTimeEdit, QDialog
)
from PySide6.QtCore import Qt, QTime
from datetime import datetime
from configuration.database import get_connection
from modules.presence.controller import enregistrer_presence
from modules.presence.liste_presence import ListePresence
from modules.dashboard.controller import log_activite
from configuration.security import get_user

class TimeDialog(QDialog):
    """Popup pour saisir l'heure avec QTimeEdit"""
    def __init__(self, title="Heure", default_time="08:15", parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setFixedSize(250, 120)

        layout = QVBoxLayout(self)

        self.label = QLabel("Choisir l'heure :")
        layout.addWidget(self.label)

        heures, minutes = map(int, default_time.split(":"))
        self.time_edit = QTimeEdit(QTime(heures, minutes))
        self.time_edit.setDisplayFormat("HH:mm")
        layout.addWidget(self.time_edit)

        self.btn_ok = QPushButton("OK")
        self.btn_ok.clicked.connect(self.accept)
        layout.addWidget(self.btn_ok)

    def get_time(self):
        return self.time_edit.time().toString("HH:mm")

class TableauPresenceView(QWidget):
    """Vue tableau de présence adaptée au style CalculSalaireView"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self.getStyleSheet())
        self.load_employes
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

        # Bouton nouvelle presence
        self.btn_fiche = QPushButton("Liste de Présence")
        self.btn_fiche.setCursor(Qt.PointingHandCursor)
        self.btn_fiche.setStyleSheet(self.getStyleSheet())
        self.btn_fiche.clicked.connect(self.fiche)
        self.btn_reset.clicked.connect(self.reset_table)
        search_layout.addStretch()
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
                                padding: 8px;
                                font-weight: bold;
                                border: none;
                            }

                            QTableWidget::item {
                                padding: 5px;
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

    # ───────── LOGIQUE TABLEAU ─────────
    def filter_table(self):
        text = self.ent_search.text().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            nom = item.text().lower() if item else ""
            self.table.setRowHidden(row, text not in nom)

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
            action_layout.setSpacing(5)

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
                        font-size: 13px;
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
                        height: 30px;
                        font-weight: bold;
                    }
                """)

    def reset_table(self, ):
        # Parcours chaque ligne
        date = datetime.now().strftime("%Y-%m-%d")
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 3)
            if widget:  # Si la cellule a un widget (layout)
                for i in range(widget.layout().count()):
                    btn = widget.layout().itemAt(i).widget()
                    if isinstance(btn, QPushButton):
                        btn.setEnabled(True)

                        # Ré-applique le style en fonction du texte du bouton
                        if btn.text() == "Présent":
                            color = "#4da6ff"
                        elif btn.text() == "Absent":
                            color = "#6699cc"
                        elif btn.text() == "Retard":
                            color = "#3399ff"
                        elif btn.text() == "Partir tôt":
                            color = "#1a66cc"
                        else:
                            color = "#CCCCCC"  # fallback

                        btn.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {color};
                                color: white;
                                border-radius: 5px;
                                height: 40px;
                                font-weight: bold;
                                font-size: 13px;
                            }}
                            QPushButton:hover {{
                                background-color: #004c99;
                            }}
                        """)
        enregistrer_presence(employe_id = None, date=date, heure_entree= None, heure_sortie= "Fin", statut= None)
        enregistrer_presence(employe_id = None, date=date, heure_entree=None, heure_sortie="Début", statut=None)

        user = get_user()
        log_activite(
            f" des les de présence réussie",
            module="presence",
            utilisateur=user["username"]
        )

        QMessageBox.information(self, "succès", "Fiche de présence enregistré et renouvellé")

    def fiche(self):
        self.fiche_presence = ListePresence()
        self.fiche_presence.show()

    def make_handler(self, emp_id, statut, layout):
        return lambda: self.handle_action(emp_id, statut, None, layout)

    def handle_action(self, employe_id, statut, time_edit, layout):
        date = datetime.now().strftime("%Y-%m-%d")
        heure_entree, heure_sortie = None, None

        if statut == "present":
            heure_entree, heure_sortie = "08:00", "17:00"
            QMessageBox.information(self, "Succès", "Presence enregistrée avec succès!")
        elif statut == "absent":
            QMessageBox.information(self, "Succès", "Presence enregistrée avec succès!")
        elif statut == "retard":
            dialog = TimeDialog("Heure d'arrivée", "08:15", self)
            if dialog.exec():  # OK cliqué
                heure_entree = dialog.get_time()
                QMessageBox.information(self, "Succès", "Presence enregistrée avec succès!")
                heure_sortie = "17:00"
            else:
                return  # Annulé

        elif statut == "depart":
            dialog = TimeDialog("Heure de départ", "16:45", self)
            if dialog.exec():
                heure_sortie = dialog.get_time()
                QMessageBox.information(self, "Succès", "Presence enregistrée avec succès!")
                heure_entree = "08:00"
            else:
                return

        # Enregistrement
        enregistrer_presence(employe_id, date, heure_entree, heure_sortie, statut)

        # Désactiver boutons pour cette ligne
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == str(employe_id):
                self.disable_row_buttons(self.table.cellWidget(row, 3).layout())
                break

    def getStyleSheet(self):
        return """
        
        QPushButton {
                background-color: "#0A1640";
                color: white;
                font-weight: bold;
                font-size : 15px ;
                padding: 10px 20px;
                border-radius: 5px;
                font-family: sans-serif;
            }
        QPushButton:hover   { background-color:"#1E6FD9"; }
        QPushButton:checked { background-color: "#0A1640"; }

        QLabel{
            color: black;
            font-size: 18px;
            font-family: sans-serif;
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
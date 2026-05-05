from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QAbstractItemView
)
from PySide6.QtCore import Qt

from modules.employe.controller import EmployeController
from modules.employe.formulaire import EmployeFormulaire
from .detail import EmployeDetail

class EmployeListe(QWidget):
    def __init__(self, controller: EmployeController):
        super().__init__()
        self.controller = controller
        self.employes = []
        self.init_ui()
        self.rafraichir()
        self.controller.liste_changed.connect(self.rafraichir)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        # -------- En-tête --------
        header = QHBoxLayout()
        header.addStretch()

        #Indice
        self.indice = QLabel("Double cliquer sur un employé pour voir tout les details ")
        self.indice.setStyleSheet("""
        QLabel {
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ddd;
            color: black;
            font-family: sans-serif;
        }
        """)
        self.indice.setAlignment(Qt.AlignCenter)
        # Bouton ajouter
        self.btn_ajouter = QPushButton("➕ Nouvel employé")
        self.btn_ajouter.setStyleSheet("""
            QPushButton {
                background-color: "#0A1640";
                color: white;
                font-weight: bold;
                font-size : 15px ;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover   { background-color:"#1E6FD9"; }
            QPushButton:checked { background-color: "#1E6FD9"; }
        """)
        self.btn_ajouter.clicked.connect(self.ajouter)
        header.addWidget(self.btn_ajouter)

        # Bouton rafraîchir
        self.btn_rafraichir = QPushButton("🔄 Rafraîchir")
        self.btn_rafraichir.setStyleSheet("""
            QPushButton {
                background-color: "#0A1640";
                color: white;
                font-weight: bold;
                font-size : 15px ;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover   { background-color:"#1E6FD9"; }
            QPushButton:clicked { background-color: "#1E6FD9"; }
        """)
        self.btn_rafraichir.clicked.connect(self.rafraichir)
        header.addWidget(self.btn_rafraichir)

        layout.addLayout(header)

        # -------- Recherche --------
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom, prénom ou email...")
        self.search_input.setFixedWidth(500)
        self.search_input.setStyleSheet("""
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
        self.search_input.textChanged.connect(self.rechercher)

        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        search_layout.addWidget(self.btn_ajouter)
        search_layout.addWidget(self.btn_rafraichir)
        layout.addWidget(search_frame)

        # -------- Tableau --------
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Prénoms","Poste", "Email", "Téléphone"])

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

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.doubleClicked.connect(self.ouvrir_detail)
        layout.addWidget(self.table)

        # -------- Statistiques --------
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #6B7280; padding: 10px;")
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.indice)

    # -------- Rafraîchir et afficher --------
    def rafraichir(self):
        self.employes = self.controller.get_liste()
        self.afficher(self.employes)
        self.mettre_a_jour_stats()

    def afficher(self, employes):
        self.table.setRowCount(max(len(employes), 1))  # Au moins 1 ligne

        if not employes:  # Aucun résultat
            self.table.setItem(0, 0, QTableWidgetItem("Aucun résultat"))
            for col in range(1, self.table.columnCount()):
                self.table.setItem(0, col, QTableWidgetItem(""))  # colonnes vides
            # Centrer le texte
            self.table.item(0, 0).setTextAlignment(Qt.AlignCenter)
        else:
            for i, emp in enumerate(employes):
                self.table.setItem(i, 0, QTableWidgetItem(str(emp.get('id', ''))))
                self.table.setItem(i, 1, QTableWidgetItem(emp.get('prenom', '')))
                self.table.setItem(i, 2, QTableWidgetItem(emp.get('nom', '')))
                self.table.setItem(i, 3, QTableWidgetItem(emp.get('poste', '')))
                self.table.setItem(i, 4, QTableWidgetItem(emp.get('email', '')))
                self.table.setItem(i, 5, QTableWidgetItem(emp.get('telephone', '')))

                # Centrer tout le texte
                for col in range(self.table.columnCount()):
                    self.table.item(i, col).setTextAlignment(Qt.AlignCenter)

                # Numéro de ligne
                self.table.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))

        self.table.resizeColumnsToContents()

    # -------- Recherche --------
    def rechercher(self, texte):
        if not texte.strip():
            self.afficher(self.employes)
        else:
            resultats = self.controller.rechercher(texte)
            self.afficher(resultats)

    # -------- Ajouter un employé --------
    def ajouter(self):
        self.form = EmployeFormulaire(self.controller)
        self.form.employe_sauvegarde.connect(self.rafraichir)
        self.form.show()

    # -------- Ouvrir le détail --------
    def ouvrir_detail(self, index):
        emp_id = int(self.table.item(index.row(), 0).text())
        employe = self.controller.get_employe(emp_id)
        if employe:
            self.detail = EmployeDetail(self.controller, employe)
            self.detail.employe_modifie.connect(self.rafraichir)
            self.detail.employe_supprime.connect(self.rafraichir)
            self.detail.show()

    # -------- Mettre à jour les statistiques --------
    def mettre_a_jour_stats(self):
        stats = self.controller.get_statistiques()
        self.stats_label.setText(
            f"📊 Total: {stats['total']} employés | "
            f"✅ Actifs: {stats['actifs']} | "
            f"💰 Masse salariale: {stats['total_salaire']:,.0f} Ar"
        )
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QAbstractItemView,QComboBox
)
from PySide6.QtCore import Qt

from modules.employe.controller import EmployeController
from modules.employe.formulaire import EmployeFormulaire
from modules.employe.detail import EmployeDetail
from modules.employe.model import EmployeModel
from modules.dashboard.controller import log_activite

class EmployeListe(QWidget):
    def __init__(self, controller: EmployeController):
        super().__init__()
        self.controller = controller
        self.model = EmployeModel()
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
        self.indice.setStyleSheet(self.getStyleSheet())
        self.indice.setAlignment(Qt.AlignCenter)

        self.cb_poste = QComboBox()
        self.cb_poste.addItem("Tous les poste", None)
        self.cb_poste.setStyleSheet("color: black; padding: 8px;border: 1px solid #C2D4E8; border-radius: 5px; background-color: white; min-width: 200px; font-family: sans serif;")

        postes = self.model.get_postes_uniques()

        for poste in postes:
            self.cb_poste.addItem(poste, poste)

        self.cb_poste.currentIndexChanged.connect(self.filtrer_par_poste)

        self.cb_contrat = QComboBox()

        self.cb_contrat.addItems([
            "Tous contrats",
            "CDI",
            "CDD",
            "Stage",
            "Freelance",
            "Consultant"
        ])

        self.cb_contrat.setStyleSheet(
            "color: black; padding: 8px;"
            "border: 1px solid #C2D4E8;"
            "border-radius: 5px;"
            "background-color: white;"
            "min-width: 180px;"
            "font-family: sans serif;"
        )

        self.cb_contrat.currentIndexChanged.connect(
            self.filtrer_contrat
        )

        # Bouton ajouter
        self.btn_ajouter = QPushButton("➕ Nouvel employé")
        self.btn_ajouter.setStyleSheet(self.getStyleSheet())
        self.btn_ajouter.clicked.connect(self.ajouter)
        header.addWidget(self.btn_ajouter)

        # Bouton rafraîchir
        self.btn_rafraichir = QPushButton("🔄 Rafraîchir")
        self.btn_rafraichir.setStyleSheet(self.getStyleSheet())
        self.btn_rafraichir.clicked.connect(self.rafraichir)
        header.addWidget(self.btn_rafraichir)

        layout.addLayout(header)

        # -------- Recherche --------
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom, prénom ou email...")
        self.search_input.setFixedWidth(500)
        self.search_input.setStyleSheet(self.getStyleSheet())
        self.search_input.textChanged.connect(self.rechercher)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.cb_poste)
        search_layout.addWidget(self.cb_contrat)
        search_layout.addStretch()
        search_layout.addWidget(self.btn_ajouter)
        search_layout.addWidget(self.btn_rafraichir)
        layout.addWidget(search_frame)

        # -------- Tableau --------
        self.table = QTableWidget()
        self.table.setColumnCount(9)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Nom",
            "Prénoms",
            "Poste",
            "Contrat",
            "Fin contrat",
            "Heure/Jour",
            "Email",
            "Téléphone"
        ])
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
        self.table.setStyleSheet(self.getStyleSheet())

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

    def filtrer_par_poste(self):
        poste = self.cb_poste.currentData()

        log_activite(
            f"Filtrage poste: {poste}",
            module="employe",
            utilisateur="system"
        )

        if poste is None:
            self.afficher(self.employes)
        else:
            resultats = [
                emp for emp in self.employes
                if emp.get("poste") == poste
            ]
            self.afficher(resultats)

    def afficher(self, employes):

        self.table.setRowCount(max(len(employes), 1))

        if not employes:

            self.table.setItem(
                0,
                0,
                QTableWidgetItem("Aucun résultat")
            )

            for col in range(
                    1,
                    self.table.columnCount()
            ):
                self.table.setItem(
                    0,
                    col,
                    QTableWidgetItem("")
                )

            self.table.item(0, 0).setTextAlignment(
                Qt.AlignCenter
            )

        else:

            for i, emp in enumerate(employes):

                self.table.setItem(
                    i,
                    0,
                    QTableWidgetItem(
                        str(emp.get('id', ''))
                    )
                )

                self.table.setItem(
                    i,
                    1,
                    QTableWidgetItem(
                        emp.get('nom', '')
                    )
                )

                self.table.setItem(
                    i,
                    2,
                    QTableWidgetItem(
                        emp.get('prenom', '')
                    )
                )

                self.table.setItem(
                    i,
                    3,
                    QTableWidgetItem(
                        emp.get('poste', '')
                    )
                )

                self.table.setItem(
                    i,
                    4,
                    QTableWidgetItem(
                        emp.get(
                            'type_contrat',
                            ''
                        )
                    )
                )

                self.table.setItem(
                    i,
                    5,
                    QTableWidgetItem(
                        str(
                            emp.get(
                                'date_fin_contrat',
                                ''
                            )
                        )
                    )
                )

                self.table.setItem(
                    i,
                    6,
                    QTableWidgetItem(
                        str(
                            emp.get(
                                'heure_travail',
                                ''
                            )
                        )
                    )
                )

                self.table.setItem(
                    i,
                    7,
                    QTableWidgetItem(
                        emp.get('email', '')
                    )
                )

                self.table.setItem(
                    i,
                    8,
                    QTableWidgetItem(
                        emp.get(
                            'telephone',
                            ''
                        )
                    )
                )

                # Centrage

                for col in range(
                        self.table.columnCount()
                ):

                    item = self.table.item(i, col)

                    if item:
                        item.setTextAlignment(
                            Qt.AlignCenter
                        )

                # Numéro ligne

                self.table.setVerticalHeaderItem(
                    i,
                    QTableWidgetItem(str(i + 1))
                )

        self.table.resizeColumnsToContents()

    # -------- Recherche --------
    def rechercher(self, texte):
        log_activite(
            f"Recherche employés: {texte}",
            module="employe",
            utilisateur="system"
        )
        if not texte.strip():
            self.afficher(self.employes)
        else:
            resultats = self.controller.rechercher(texte)
            self.afficher(resultats)

    # -------- Ajouter un employé --------
    def ajouter(self):
        log_activite(
            "Ouverture formulaire ajout employé",
            module="employe",
            utilisateur="system"
        )

        self.form = EmployeFormulaire(self.controller)
        self.form.employe_sauvegarde.connect(self.rafraichir)
        self.form.show()

    # -------- Ouvrir le détail --------
    def ouvrir_detail(self, index):
        emp_id = (self.table.item(index.row(), 0).text())
        employe = self.controller.get_employe(emp_id)
        log_activite(
            f"Consultation employé ID {emp_id}",
            module="employe",
            utilisateur="system"
        )

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

    def filtrer_contrat(self):

        contrat = self.cb_contrat.currentText()

        if contrat == "Tous contrats":
            self.afficher(self.employes)

            return

        resultats = [

            emp for emp in self.employes

            if emp.get("type_contrat") == contrat
        ]

        self.afficher(resultats)

        log_activite(
            f"Filtrage contrat: {contrat}",
            module="employe",
            utilisateur="system"
        )

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

    def getStyleSheet(self):
        return """

        QLabel {
            color: black;
            font-size: 14px;
            font-weight: bold;
            font-family: sans-serif;        
        }

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

        QTextEdit {
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ddd;
            color: black;
            font-family: sans-serif;
        }

        QLineEdit:focus {
            border: 1px solid #1877f2;
        }

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

        #btn_close {
            background: transparent;
            color: red;
            font-size: 20px;
        }
        #titre{
            color: black;
            font-size: 28px;
            font-weight: bold;
            font-family: sans-serif;
        }
        QComboBox {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 5px;
            background-color: white;
            color: black;  /* couleur du texte sélectionné */
            font-size: 14px;
            font-family: sans-serif;
        }
        QComboBox QAbstractItemView {
            background-color: white;  
            color: black;            
            selection-background-color: #1877f2;
            selection-color: black;            
        }
        QComboBox::drop-down {
            border: none;
        }

        QMessageBox {
                background-color: #F6F8FB;
                border-radius: 6px;
            }

            QMessageBox QLabel {
                color: #0A1640;
                font-size: 15px;
                font-weight: bold;
                font-family: sans-serif;
                min-width: 250px;
            }

            QMessageBox QPushButton {
                background-color: #0A1640;
                color: white;
                border-radius: 6px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }

            QMessageBox QPushButton:hover {
                background-color: #1E6FD9;
            }

            QMessageBox QPushButton:pressed {
                background-color: #163E73;
            }
            
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
        """
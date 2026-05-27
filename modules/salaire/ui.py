#ui salaire
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QHeaderView, QTableWidget, QTableWidgetItem, QFrame, QStackedWidget,
    QFormLayout, QComboBox, QDoubleSpinBox, QScrollArea,QAbstractItemView, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from modules.dashboard.controller import log_activite
from modules.salaire.avance_conge import AvanceCongeForm
from modules.salaire.model import get_employes, get_employe_by_id, calculer_salaire_complet, get_conges, get_avances, enregistrer_salaire
from modules.salaire.controller import generer_bulletin_pdf
from modules.salaire.model import get_salaire_paye
from configuration.database import get_connection
from datetime import datetime
from configuration.audit_model import AuditModel
from configuration.security import get_user


# ─────────────────────────────────────────────
# Tableau des salaires
# ─────────────────────────────────────────────
class TableauSalaireView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audit = AuditModel()
        self.setStyleSheet("background-color: #f8f9fa;")
        self.salaires = []
        self._build()
        self._charger_donnees()  # charger dès le début

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Zone de recherche ---
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(20, 20, 20, 20)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom, prénom ou email...")
        self.search_input.setFixedWidth(500)
        self.search_input.setStyleSheet(
            """QLineEdit {
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

        # ─── FILTRE MOIS ───
        self.cb_mois = QComboBox()
        self.cb_mois.setStyleSheet("""
           QComboBox {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 4px 8px;
                color: black;
            }
        """)
        self.cb_mois.addItem("Tous les mois", "")
        current_year = datetime.now().strftime("%Y")
        for i in range(1, 13):
            self.cb_mois.addItem(f"{current_year}-{i:02d}", f"{current_year}-{i:02d}")

        # ─── FILTRE STATUT ───
        self.cb_statut = QComboBox()
        self.cb_statut.addItems([
            "Tous",
            "EN_ATTENTE",
            "Approuvé",
            "Rejetté"
        ])
        self.cb_statut.setStyleSheet("""
                QComboBox {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 4px 8px;
                color: black;
            }
                """)
        self.cb_mois.currentIndexChanged.connect(self.appliquer_filtres)
        self.cb_statut.currentIndexChanged.connect(self.appliquer_filtres)

        # Ajouter dans le layout
        search_layout.addWidget(self.cb_mois)
        search_layout.addWidget(self.cb_statut)

        btn_action = QPushButton("Autre action")
        btn_action.setCursor(Qt.PointingHandCursor)
        btn_action.setStyleSheet("""
            QPushButton {
                    background-color: #0A1640;
                    color: white;
                    font-weight: bold;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-family: sans serif;
                }
                QPushButton:hover { background-color:#1E6FD9; }
        """)
        btn_action.clicked.connect(self.avance_conges)
        layout.addWidget(search_container)
        search_layout.addStretch()
        search_layout.addWidget(btn_action)

        # --- Table ---
        self.table = QTableWidget()
        columns = ["ID", "Nom", "Prénom", "Mois", "Salaire Base", "Primes", "Retenues", "Net à Payer", "Statut","Action"]
        self.table.setColumnCount(len(columns))
        # Numéro de ligne (vertical header)
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setDefaultSectionSize(30)
        # Sélection par ligne entière
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Désactiver édition
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Supprimer focus (cadre au clic)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setHorizontalHeaderLabels(columns)
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

        hdr = self.table.horizontalHeader()
        for i in range(len(columns)):
            hdr.setSectionResizeMode(i, QHeaderView.Stretch)

        table_wrap = QVBoxLayout()
        table_wrap.setContentsMargins(10, 0, 10, 0)
        table_wrap.addWidget(self.table)
        layout.addLayout(table_wrap)

    def actualiser(self):
        self._charger_donnees()
        self.load_salaire(self.salaires)

    def appliquer_filtres(self):
        texte = self.search_input.text().lower()
        mois = self.cb_mois.currentData()
        statut = self.cb_statut.currentText()

        resultats = []

        for emp in self.salaires:

            # 🔍 FILTRE TEXTE
            if texte:
                if not (
                        texte in str(emp["id"]) or
                        texte in emp["nom"].lower() or
                        texte in emp["prenom"].lower() or
                        texte in emp.get("mois", "").lower() or
                        texte in emp.get("statut", "").lower()
                ):
                    continue

            # 📅 FILTRE MOIS
            if mois and emp["mois"] != mois:
                continue

            # 📌 FILTRE STATUT
            if statut != "Tous" and emp["statut"] != statut:
                continue

            resultats.append(emp)

        self.load_salaire(resultats)

# ✅ Charger données

    def _charger_donnees(self):
        self.salaires = get_salaire_paye(None)

        print("DEBUG résultats =", self.salaires)

        if not self.salaires:
            print("Aucune donnée trouvée pour ce mois")
            self.load_salaire([])
            return

        self.load_salaire(self.salaires)

    def filtrer_mois(self, mois):
        filtered = [s for s in self.salaires if s["mois"] == mois]
        self.load_salaire(filtered)

    # ✅ Affichage
    def load_salaire(self, salaires):
        self.table.setRowCount(max(len(salaires), 1))  # Au moins 1 ligne

        if not salaires:  # Aucun résultat
            self.table.setItem(0, 0, QTableWidgetItem("Aucun résultat"))
            for col in range(1, self.table.columnCount()):
                self.table.setItem(0, col, QTableWidgetItem(""))
            self.table.item(0, 0).setTextAlignment(Qt.AlignCenter)
            return

        for i, emp in enumerate(salaires):
            # Remplissage des colonnes
            self.table.setItem(i, 0, QTableWidgetItem(str(emp["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(emp["nom"]))
            self.table.setItem(i, 2, QTableWidgetItem(emp["prenom"]))
            self.table.setItem(i, 3, QTableWidgetItem(emp["mois"]))
            self.table.setItem(i, 4, QTableWidgetItem(str(emp["salaire_base"])))
            self.table.setItem(i, 5, QTableWidgetItem(str(emp["bonus"])))
            self.table.setItem(i, 6, QTableWidgetItem(str(emp["deduction"])))
            self.table.setItem(i, 7, QTableWidgetItem(str(emp["salaire_net"])))
            self.table.setItem(i, 8, QTableWidgetItem(emp["statut"]))
            # Centrer texte
            for col in range(self.table.columnCount()):
                item = self.table.item(i, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)

            # Numéro de ligne
            self.table.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))

            # ================= ACTIONS =================
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(2)

            btn_approuver = QPushButton("Approuver")
            btn_rejetter = QPushButton("Rejetter")

            for btn, color in zip(
                    [btn_approuver, btn_rejetter],
                    ["#4da6ff", "#6699cc"]
            ):
                btn.setStyleSheet(f"""
                                    QPushButton {{
                                        background-color: {color};
                                        color: white;
                                        padding: 0;
                                        border-radius: 5px;
                                        height: 40px;
                                        font-weight: bold;
                                        font-size: 11px;
                                    }}
                                    QPushButton:hover {{
                                        background-color: #004c99;
                                    }}
                                """)
            # ✅ ID correct
            emp_id = emp.get("id")
            mois = emp["mois"]

            # Connexions
            btn_approuver.clicked.connect(
                self.make_handler(emp_id, mois, "Approuvé", action_layout)
            )

            btn_rejetter.clicked.connect(
                self.make_handler(emp_id, mois, "Rejetté", action_layout)
            )

            # ✅ Désactivation permanente si déjà traité
            if emp["statut"] != "EN_ATTENTE":
                btn_approuver.setEnabled(False)
                btn_rejetter.setEnabled(False)

                btn_approuver.setStyleSheet("""
                    QPushButton {
                        background-color: #cccccc;
                        color: #666666;
                        border-radius: 5px;
                        padding:0;
                        height: 30px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                """)

                btn_rejetter.setStyleSheet("""
                    QPushButton {
                        background-color: #cccccc;
                        color: #666666;
                        border-radius: 5px;
                        padding:0;
                        height: 30px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                """)

            action_layout.addWidget(btn_approuver)
            action_layout.addWidget(btn_rejetter)
            action_widget.setLayout(action_layout)

            # ✅ IMPORTANT : setCellWidget et BON INDEX
            self.table.setCellWidget(i, 9, action_widget)

        self.table.resizeColumnsToContents()

    def make_handler(self, emp_id, mois, statut, layout):
        return lambda: self.handle_action(emp_id, mois, statut, layout)

    def handle_action(self, emp_id, mois, statut, layout):

        user = get_user()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE salaire
            SET statut = ?
            WHERE employe_id = ?
            AND mois = ?
        """, (statut, emp_id, mois))

        conn.commit()

        # 🔥 LOG ACTIVITE (comme avance_congé)
        log_activite(
            f"Validation salaire {statut} - employé {emp_id} ({mois})",
            module="salaire",
            utilisateur=user["username"]
        )

        # 🔥 AUDIT TRAÇABILITÉ (IMPORTANT)
        self.audit.log(
            action="UPDATE",
            table="salaire",
            record_id=f"{emp_id}-{mois}",
            old_data=None,
            new_data={
                "employe_id": emp_id,
                "mois": mois,
                "statut": statut
            },
            utilisateur=user["username"]
        )

        conn.close()

        msg = QMessageBox(self)
        msg.setWindowTitle("Succès")
        msg.setText(f"Validation salaire {statut} \n employé {emp_id}")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(self.styled_messagebox())
        msg.exec()

        self._charger_donnees()


    # ✅ Recherche AUTO (temps réel)
    def rechercher(self, texte):
        texte = texte.lower()

        if not texte:
            self.load_salaire(self.salaires)
            return

        resultats = [
            emp for emp in self.salaires
            if texte in str(emp["id"])
               or texte in emp["nom"].lower()
               or texte in emp["prenom"].lower()
               or texte in emp.get("mois", "").lower()
               or texte in emp.get("statut", "").lower()
        ]

        self.load_salaire(resultats)

    def avance_conges(self):
        self.avance = AvanceCongeForm()
        self.avance.show()

    def get_selected_row_data(self):
        selected = self.table.currentRow()

        if selected == -1:
            return None

        emp_id_item = self.table.item(selected, 0)
        mois_item = self.table.item(selected, 3)

        if not emp_id_item or not mois_item:
            return None

        return {
            "emp_id": (emp_id_item.text()),
            "mois": mois_item.text()
        }

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

# ─────────────────────────────────────────────
# Formulaire de calcul
# ─────────────────────────────────────────────
class FormCalculSalaireView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_view = parent
        self.audit = AuditModel()
        self.setStyleSheet("background-color: #f8f9fa;")
        self._build()

    def _spinbox(self, suffix=" Ar", decimals=2, maximum=9_999_999):
        sb = QDoubleSpinBox()
        sb.setDecimals(decimals)
        sb.setMaximum(maximum)
        sb.setSuffix(suffix)
        sb.setValue(0)
        sb.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                color : black;
                border: 1px solid #C2D4E8;
                border-radius: 5px;
                background-color: white;
                min-width: 200px;
            }
        """)
        return sb

    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl.setStyleSheet("""
            color: white;
            background-color: #0A1628;
            padding: 6px 14px;
            border-radius: 4px;
            font-family: sans serif;
        """)
        return lbl

    def _field_style(self):
        return """
            QLineEdit, QComboBox {
                padding: 8px;
                color: black;
                border: 1px solid #C2D4E8;
                border-radius: 5px;
                background-color: white;
                min-width: 200px;
                font-family: sans serif;
            }
        """

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent;font-family: sans serif; }")

        container = QWidget()
        container.setStyleSheet("background-color: #f8f9fa;")
        main = QVBoxLayout(container)
        main.setContentsMargins(30, 20, 30, 30)
        main.setSpacing(18)

        # ── Section : Informations employé ──
        main.addWidget(self._section_label("👤  Informations de l'employé"))

        form_info = QFormLayout()
        form_info.setSpacing(12)
        form_info.setLabelAlignment(Qt.AlignRight)

        self.cb_employe = QComboBox()
        self.cb_employe.setStyleSheet(self.getStyleSheet())
        self.cb_employe.addItem("Tous les employés", None)

        employes = get_employes()
        for emp in employes:
            self.cb_employe.addItem(emp[2], emp[0])

        self.cb_periode = QComboBox()
        mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        self.cb_periode.addItems(mois)
        self.cb_periode.setStyleSheet(self.getStyleSheet())

        for lbl_text, widget in [
            ("Employé :", self.cb_employe),
            ("Période (mois) :", self.cb_periode),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("color: #0A1628;")
            form_info.addRow(lbl, widget)

        main.addLayout(form_info)

        # ── Section rémunération ──
        main.addWidget(self._section_label("💰  Éléments de rémunération"))
        form_rem = QFormLayout()
        form_rem.setSpacing(12)
        form_rem.setLabelAlignment(Qt.AlignRight)

        self.sb_bonus  = self._spinbox()
        self.sb_autres_primes = self._spinbox()

        for lbl_text, widget in [
            ("Bonus :", self.sb_bonus),
            ("Autres primes :", self.sb_autres_primes),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("color: #0A1628;")
            form_rem.addRow(lbl, widget)

        main.addLayout(form_rem)

        # ── Section Retenues ──
        main.addWidget(self._section_label("📉  Retenues"))
        form_ret = QFormLayout()
        form_ret.setSpacing(12)
        form_ret.setLabelAlignment(Qt.AlignRight)

        self.lbl_avances = QLabel("0 Ar")
        self.lbl_conge = QLabel("0 Ar")
        self.sb_autres_ret = self._spinbox()

        for lbl_text, widget in [
            ("Avances :", self.lbl_avances),
            ("Congé :", self.lbl_conge),
            ("Autres retenues :", self.sb_autres_ret),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("color: #0A1628;")
            form_ret.addRow(lbl, widget)

        main.addLayout(form_ret)

        # ── Résultat Net ──
        result_frame = QFrame()
        result_frame.setStyleSheet("QFrame { background-color: #0A1628; border-radius: 8px; }")
        result_layout = QHBoxLayout(result_frame)
        result_layout.setContentsMargins(20, 14, 20, 14)

        lbl_net_titre = QLabel("NET À PAYER :")
        lbl_net_titre.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_net_titre.setStyleSheet("color: #aab8c8; background: transparent;")
        self.lbl_net_valeur = QLabel("0 Ar")
        self.lbl_net_valeur.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.lbl_net_valeur.setStyleSheet("color:#aab8c8; background: transparent;")

        result_layout.addWidget(lbl_net_titre)
        result_layout.addStretch()
        result_layout.addWidget(self.lbl_net_valeur)
        main.addWidget(result_frame)

        # ── Boutons ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_reset = QPushButton("🔄 Réinitialiser")
        btn_valider = QPushButton("✅ Valider")

        for btn in [btn_reset, btn_valider]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self.getStyleSheet())

        btn_reset.clicked.connect(self._reset)

        #Valider payement
        btn_valider.clicked.connect(self._valider)

        btn_actualiser = QPushButton("Actualiser")
        btn_actualiser.setCursor(Qt.PointingHandCursor)
        btn_actualiser.setStyleSheet("""
               QPushButton {
                           background-color: #0A1640;
                           color: white;
                           font-weight: bold;
                           padding: 10px 20px;
                           border-radius: 5px;
                           font-family: sans serif;
                       }
                       QPushButton:hover { background-color:#1E6FD9; }
               """)

        btn_actualiser.clicked.connect(self._charger_donnees)
        btn_row.addWidget(btn_actualiser)
        btn_row.addWidget(btn_reset)
        btn_row.addWidget(btn_valider)
        main.addLayout(btn_row)

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        # ── Connexions
        self.cb_employe.currentIndexChanged.connect(self._charger_donnees)
        self.cb_periode.currentIndexChanged.connect(self._charger_donnees)

        self.sb_bonus.valueChanged.connect(self._calculer_auto)
        self.sb_autres_primes.valueChanged.connect(self._calculer_auto)
        self.sb_autres_ret.valueChanged.connect(self._calculer_auto)

    # ── LOGIQUE ──
    def _charger_donnees(self):
        employe_id = self.cb_employe.currentData()

        if employe_id is None:
            return

        mois = f"2026-{self.cb_periode.currentIndex() + 1:02d}"

        data = calculer_salaire_complet(employe_id, mois)

        if not data:
            return

        print("DATA:", data)

        def to_float(x):
            try:
                return float(str(x).replace(" ", "").replace(",", "."))
            except:
                return 0.0

        self.salaire_base = to_float(data["base"])
        self.retenues_auto = to_float(data["deductions"])

        self.avances = to_float(data["avances"])
        self.conges = to_float(data["conges"])


        self.lbl_avances.setText(f"{self.avances:,.0f} Ar")
        self.lbl_conge.setText(f"{self.conges:,.0f} Ar")
        self.salaire_reel = to_float(data["salaire_reel"])
        self._calculer_auto()

    def _calculer_auto(self):
        if not hasattr(self, "salaire_reel"):
            return

        def safe(x):
            try:
                return float(str(x).replace(" ", "").replace(",", "."))
            except:
                return 0.0

        salaire_reel = safe(self.salaire_reel)
        retenues_auto = safe(self.retenues_auto)
        avances = safe(self.avances)
        conges = safe(self.conges)

        primes = self.sb_bonus.value() + self.sb_autres_primes.value()
        autres_ret = self.sb_autres_ret.value()

        total_deductions = retenues_auto + avances + conges + autres_ret

        net = salaire_reel + primes - total_deductions
        net = max(0, net)

        self.lbl_net_valeur.setText(f"{net:,.0f} Ar")


    def _reset(self):
        self.sb_bonus.setValue(0)
        self.sb_autres_primes.setValue(0)
        self.sb_autres_ret.setValue(0)
        self.lbl_net_valeur.setText("0 Ar")

    def _valider(self):
        employe_id = self.cb_employe.currentData()
        if employe_id is None:
            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText("Sélectionner un employé")
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(self.styled_messagebox())
            msg.exec()
            return

        mois_sql = f"2026-{self.cb_periode.currentIndex() + 1:02d}"

        data = calculer_salaire_complet(employe_id, mois_sql)
        if not data:
            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText("Impossible de calculer le salaire")
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(self.styled_messagebox())
            msg.exec()
            return

        # ✅ NORMALISATION DES TYPES (IMPORTANT)
        def to_float(x):
            try:
                return float(str(x).replace(" ", "").replace(",", "."))
            except:
                return 0.0

        primes = self.sb_bonus.value() + self.sb_autres_primes.value()
        autres_ret = self.sb_autres_ret.value()

        deductions_auto = to_float(data.get("deductions"))
        avances = to_float(data.get("avances"))
        conges = to_float(data.get("conges"))
        salaire_reel = to_float(data.get("salaire_reel"))
        base = to_float(data.get("base"))

        total_deductions = deductions_auto + avances + conges + autres_ret

        net = salaire_reel + primes - total_deductions
        net = max(0, net)

        enregistrer_salaire(
            employe_id,
            mois_sql,
            {
                "base": base,
                "primes": primes,
                "deductions": total_deductions,
                "net": net,
                "statut": "EN_ATTENTE"
            }
        )

        msg = QMessageBox(self)
        msg.setWindowTitle("Succès")
        msg.setText(f"Salaire de {employe_id} enregistré (EN ATTENTE)")
        msg.setStyleSheet(self.styled_messagebox())
        msg.exec()

        user = get_user()

        log_activite(
            f"Enregistrement salaire employé {employe_id}",
            module="salaire",
            utilisateur=user["username"]
        )

        self.audit.log(
            action="INSERT",
            table="salaire",
            record_id=f"{employe_id}-{mois_sql}",
            old_data=None,
            new_data={
                "employe_id": employe_id,
                "mois": mois_sql,
                "base": base,
                "primes": primes,
                "deductions": total_deductions,
                "net": net,
                "statut": "EN_ATTENTE"
            },
            utilisateur=user["username"]
        )

        self.parent().parent().vue_tableau._charger_donnees()
        self.parent_view.stack.setCurrentIndex(0)

    def getStyleSheet(self):
        return """
        QPushButton {
            background-color: #0A1640;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
            font-family: sans-serif;
        }

        QPushButton:hover {
            background-color: #1E6FD9;
        }

        QLabel {
            color: #0A1628;
            font-family: sans-serif;
        }

        QLineEdit, QComboBox, QDoubleSpinBox {
            padding: 8px;
            border: 1px solid #C2D4E8;
            border-radius: 5px;
            background-color: white;
            font-family: sans-serif;
            color: black;
        }

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
        QMessageBox {
            background-color: #EDF3FB;
            font-size: 13px;
        }
        """
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
# ─────────────────────────────────────────────
# Vue principale avec QStackedWidget
# ─────────────────────────────────────────────
class CalculSalaireView(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.audit = AuditModel()
        self.setStyleSheet("background-color: #f8f9fa;")
        self._build()

    def _build(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: white; border-bottom: 1px solid #C2D4E8;")
        header_layout = QHBoxLayout(header)
        self.lbl_titre = QLabel("Calcul et Gestion des Salaires")
        self.lbl_titre.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.lbl_titre.setStyleSheet("color: #2c3e50; border: none;")
        header_layout.addWidget(self.lbl_titre)
        header_layout.addStretch()
        self.main_layout.addWidget(header)

        # Stack
        self.stack = QStackedWidget()
        self.vue_tableau = TableauSalaireView()
        self.vue_formule = FormCalculSalaireView(self)
        self.stack.addWidget(self.vue_tableau)
        self.stack.addWidget(self.vue_formule)
        self.main_layout.addWidget(self.stack)

        # Actions
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(20, 14, 20, 14)
        actions_layout.addStretch()

        self.btn_calcul = QPushButton("🧮  Calcul Salaire")
        self.btn_calcul.setCursor(Qt.PointingHandCursor)
        self.btn_calcul.setCheckable(True)
        self.btn_calcul.setStyleSheet("""
            QPushButton {
                    background-color: #0A1640;
                    color: white;
                    font-weight: bold;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-family: sans serif;
            }
            QPushButton:hover { background-color:#1E6FD9; }
        """)
        self.btn_calcul.clicked.connect(self._toggle_vue)

        btn_export = QPushButton("📄  Exporter PDF")
        btn_export.clicked.connect(self.exporter_liste_excel)
        btn_generer = QPushButton("+ Générer Bulletin")

        for btn in [btn_export, btn_generer]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self.getStyleSheet())

        btn_generer.clicked.connect(self.generer_depuis_table)

        actions_layout.addWidget(self.btn_calcul)
        actions_layout.addWidget(btn_export)
        actions_layout.addWidget(btn_generer)
        self.main_layout.addWidget(actions_container)

    def generer_depuis_table(self):
        from PySide6.QtWidgets import QFileDialog
        from PySide6.QtCore import QStandardPaths
        import os

        data = self.vue_tableau.get_selected_row_data()

        if not data:
            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText("Veuillez sélectionner au moins une ligne")
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(self.getStyleSheet())
            msg.exec_()
            return

        emp = get_employe_by_id(data["emp_id"])
        if not emp:
            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText(f"Employé {emp} introuvable")
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(self.getStyleSheet())
            msg.exec_()
            return

        mois_sql = data["mois"]

        salaire = calculer_salaire_complet(data["emp_id"], mois_sql)
        if not salaire:
            QMessageBox.warning(self, "Erreur", "Calcul impossible")
            msg = QMessageBox(self)
            msg.setWindowTitle("Erreur")
            msg.setText("Impossible de calculer")
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(self.getStyleSheet())
            msg.exec_()
            return

        # 📂 Documents par défaut
        default_dir = os.path.join(os.path.expanduser("~"), "Documents")
        default_file = os.path.join(
            default_dir,
            f"BULLETIN_{emp[0]}_{mois_sql}.pdf"
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le bulletin",
            default_file,
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return
        if not file_path.endswith(".pdf"):
            file_path += ".pdf"

        # ✅ DATA PROPRE ET COMPLET
        paiement_data = {
            "base": salaire["base"],
            "salaire_reel": salaire["salaire_reel"],
            "primes": salaire["primes"],
            "avances": salaire["avances"],
            "conges": salaire["conges"],
            "deductions": salaire["deductions"],
            "net": salaire["net"]
        }

        # ✅ APPEL CORRIGÉ (ORDRE IMPORTANT)
        generer_bulletin_pdf(
            emp[0],  # id
            emp[1],  # nom
            emp[2],  # prénom
            mois_sql,
            paiement_data,
            filename=file_path
        )

        msg = QMessageBox(self)
        msg.setWindowTitle("Succès")
        msg.setText(f"Bulletin de {emp[2]} généré dans :\n{file_path}")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(self.getStyleSheet())
        msg.exec_()
        user = get_user()

        log_activite(
            f"Génération bulletin {emp[1]} ({emp[0]})",
            module="salaire",
            utilisateur=user["username"]
        )

        self.audit.log(
            action="EXPORT",
            table="bulletin",
            record_id=f"{emp[0]}-{mois_sql}",
            old_data=None,
            new_data=paiement_data,
            utilisateur=user["username"]
        )
    def _toggle_vue(self, checked: bool):
        if checked:
            self.stack.setCurrentIndex(1)
            self.lbl_titre.setText("Calcul de Salaire")
            self.btn_calcul.setText("← Retour au tableau")
        else:
            self.stack.setCurrentIndex(0)
            self.lbl_titre.setText("Calcul et Gestion des Salaires")
            self.btn_calcul.setText("🧮  Calcul Salaire")

    def exporter_liste_excel(self):
        from openpyxl import Workbook
        from PySide6.QtWidgets import QFileDialog
        import os

        # 📂 dossier Documents

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le fichier Excel",
            os.path.join(os.path.expanduser("~"), "Documents"),
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        if not file_path.endswith(".xlsx"):
            file_path += ".xlsx"

        wb = Workbook()
        ws = wb.active
        ws.title = "Salaires"

        table = self.vue_tableau.table

        # HEADER
        headers = []
        for col in range(table.columnCount()):
            item = table.horizontalHeaderItem(col)
            headers.append(item.text() if item else "")
        ws.append(headers)

        # DATA
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                row_data.append(item.text() if item else "")
            ws.append(row_data)

        wb.save(file_path)

        msg = QMessageBox(self)
        msg.setWindowTitle("Succès")
        msg.setText(f"Export Excel terminé :\n{file_path}")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(self.getStyleSheet())
        msg.exec_()
        user = get_user()

        log_activite(
            "Export Excel des salaires",
            module="salaire",
            utilisateur=user["username"]
        )

        self.audit.log(
            action="EXPORT",
            table="salaire",
            record_id="ALL",
            old_data=None,
            new_data={"format": "xlsx"},
            utilisateur=user["username"]
        )

    def getStyleSheet(self):
        return """
         QMessageBox {
            background-color: #EDF3FB;
            font-size: 13px;
        }
        
        QPushButton {
            background-color: #0A1640;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
            font-family: sans-serif;
        }

        QPushButton:hover {
            background-color: #1E6FD9;
        }

        QLabel {
            color: #0A1628;
            font-family: sans-serif;
        }

        QLineEdit, QComboBox, QDoubleSpinBox {
            padding: 8px;
            border: 1px solid #C2D4E8;
            border-radius: 5px;
            background-color: white;
            font-family: sans-serif;
        }

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
        """
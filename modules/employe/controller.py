from PySide6.QtCore import QObject, Signal

from modules.employe.model import EmployeModel

from modules.dashboard.controller import log_activite
from configuration.security import get_user
from configuration.audit_model import AuditModel
audit = AuditModel()

class EmployeController(QObject):

    # ==================================================
    # SIGNALS
    # ==================================================

    liste_changed = Signal(list)

    # ==================================================
    # INIT
    # ==================================================

    def __init__(self):

        super().__init__()

        self.model = EmployeModel()

    # ==================================================
    # GET LISTE
    # ==================================================

    def get_liste(self):

        return self.model.get_all()

    # ==================================================
    # GET EMPLOYE
    # ==================================================

    def get_employe(self, emp_id):

        return self.model.get_by_id(emp_id)

    # ==================================================
    # AJOUTER
    # ==================================================

    def ajouter(self, data):

        try:

            # ----------------------------------------------
            # VERIFICATION ID EXISTANT
            # ----------------------------------------------

            exist = self.model.get_by_id(data["id"])

            if exist:

                return {
                    "success": False,
                    "error": "Identifiant déjà utilisé"
                }

            # ----------------------------------------------
            # CREATION
            # ----------------------------------------------

            emp_id = self.model.create(data)

            if not emp_id:

                return {
                    "success": False,
                    "error": "Erreur création employé"
                }

            # ----------------------------------------------
            # RECUPERATION
            # ----------------------------------------------

            employe = self.model.get_by_id(
                data["id"]
            )

            # ----------------------------------------------
            # EMIT
            # ----------------------------------------------

            self.liste_changed.emit(
                self.get_liste()
            )

            # ----------------------------------------------
            # LOG
            # ----------------------------------------------
            user = get_user()
            username = user["username"] if user else "unknown"

            log_activite(
                f"Ajout employé : "
                f"{data['nom']} "
                f"{data['prenom']}",
                module="employe",
                utilisateur=username
            )

            audit.log(
                action="AJOUT",
                table="employes",
                record_id=data["id"],
                old_data=None,
                new_data=data,
                utilisateur=username
            )

            return {
                "success": True,
                "employe": employe
            }

        except Exception as e:

            log_activite(
                f"Erreur ajout employé : {str(e)}",
                module="employe",
                utilisateur="system"
            )

            return {
                "success": False,
                "error": str(e)
            }

    # ==================================================
    # MODIFIER
    # ==================================================

    def modifier(self, emp_id, data):

        try:

            employe = self.model.get_by_id(
                emp_id
            )

            if not employe:

                return {
                    "success": False,
                    "error": "Employé introuvable"
                }

            success = self.model.update(
                emp_id,
                data
            )

            if not success:

                return {
                    "success": False,
                    "error": "Modification impossible"
                }

            employe = self.model.get_by_id(
                emp_id
            )

            self.liste_changed.emit(
                self.get_liste()
            )

            user = get_user()
            username = user["username"] if user else "unknown"

            log_activite(
                f"Modification employé : "
                f"{emp_id}",
                module="employe",
                utilisateur=username
            )

            old_employe = self.model.get_by_id(emp_id)
            new_employe = self.model.get_by_id(emp_id)
            audit.log(
                action="MODIFICATION",
                table="employes",
                record_id=emp_id,
                old_data=old_employe,
                new_data=new_employe,
                utilisateur=username
            )

            return {
                "success": True,
                "employe": employe
            }

        except Exception as e:

            log_activite(
                f"Erreur modification employé : "
                f"{str(e)}",
                module="employe",
                utilisateur="system"
            )


            return {
                "success": False,
                "error": str(e)
            }

    # ==================================================
    # SUPPRIMER
    # ==================================================

    def supprimer(self, emp_id):

        try:

            employe = self.model.get_by_id(
                emp_id
            )

            if not employe:

                return {
                    "success": False,
                    "error": "Employé introuvable"
                }

            success = self.model.delete(
                emp_id
            )

            if not success:

                return {
                    "success": False,
                    "error": "Suppression impossible"
                }

            self.liste_changed.emit(
                self.get_liste()
            )

            user = get_user()
            username = user["username"] if user else "unknown"
            log_activite(
                f"Suppression employé : "
                f"{emp_id}",
                module="employe",
                utilisateur=username
            )

            audit.log(
                action="SUPPRESSION",
                table="employes",
                record_id=emp_id,
                old_data=employe,
                new_data=None,
                utilisateur=username
            )

            return {
                "success": True
            }

        except Exception as e:

            log_activite(
                f"Erreur suppression employé : "
                f"{str(e)}",
                module="employe",
                utilisateur="system"
            )

            return {
                "success": False,
                "error": str(e)
            }

    # ==================================================
    # RECHERCHE
    # ==================================================

    def rechercher(self, terme):

        try:

            user = get_user()
            username = user["username"] if user else "unknown"

            audit.log(
                action="RECHERCHER",
                table="employes",
                record_id=terme,
                utilisateur=username
            )
            return self.model.search(terme)

        except Exception as e:

            log_activite(
                f"Erreur recherche employé : "
                f"{str(e)}",
                module="employe",
                utilisateur="system"
            )

            return []

    # ==================================================
    # FILTRE PAR POSTE
    # ==================================================

    def filtrer_par_poste(self, poste):

        try:
            user = get_user()
            username = user["username"] if user else "unknown"

            audit.log(
                action="FILTER_PAR_POSTE",
                table="employes",
                record_id=poste,
                utilisateur=username
            )
            return self.model.get_by_poste(
                poste
            )

        except Exception as e:

            log_activite(
                f"Erreur filtre poste : "
                f"{str(e)}",
                module="employe",
                utilisateur="system"
            )

            return []

    # ==================================================
    # STATISTIQUES
    # ==================================================

    def get_statistiques(self):

        try:

            return self.model.get_statistiques()

        except Exception as e:

            log_activite(
                f"Erreur statistiques employé : "
                f"{str(e)}",
                module="employe",
                utilisateur="system"
            )

            return {}

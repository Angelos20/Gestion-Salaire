from PySide6.QtCore import QObject, Signal
from modules.employe.model import EmployeModel
from modules.dashboard.controller import log_activite

class EmployeController(QObject):
    # Signal qui envoie la liste des employés à la vue quand elle change
    liste_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self.model = EmployeModel()

    # Récupère tous les employés
    def get_liste(self):
        return self.model.get_all()

    # Récupère un employé par id
    def get_employe(self, emp_id):
        return self.model.get_by_id(emp_id)

    # Ajouter un nouvel employé
    def ajouter(self, data):

        emp_id = self.model.create(data)
        employe = self.model.get_by_id(emp_id)

        log_activite(
            f"Ajout d'un employé réussie",
            module="employe",
            utilisateur=emp_id
        )

        self.liste_changed.emit(self.get_liste())
        return {"success": True, "employe": employe}


    # Modifier un employé existant
    def modifier(self, emp_id, data):
        if self.model.update(emp_id, data):
            employe = self.model.get_by_id(emp_id)
            self.liste_changed.emit(self.get_liste())

            log_activite(
                f"Modification d'un employé réussie",
                module="employe",
                utilisateur=emp_id
            )

            return {"success": True, "employe": employe}
        return {"success": False, "error": "Employé non trouvé"}

    # Supprimer un employé
    def supprimer(self, emp_id):
        if self.model.delete(emp_id):
            self.liste_changed.emit(self.get_liste())

            log_activite(
                f"Suppresion d'un employé réussie",
                module="employe",
                utilisateur=emp_id
            )

            return {"success": True}
        return {"success": False, "error": "Employé non trouvé"}

    # Rechercher un employé
    def rechercher(self, terme):
        return self.model.search(terme)

    # Obtenir les statistiques
    def get_statistiques(self):
        return self.model.get_statistiques()
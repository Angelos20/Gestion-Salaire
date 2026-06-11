# 💼 Gestion Salaire

Application de gestion des ressources humaines et de la paie développée avec **Python**, **PySide6** et **SQLite**.

## 📌 Présentation

Gestion Salaire est une solution de gestion des employés permettant :

* Gestion des employés
* Gestion des présences
* Gestion des salaires
* Gestion des congés
* Gestion des avances sur salaire
* Tableau de bord statistique
* Journal des activités
* Gestion des utilisateurs
* Audit des modifications
* Configuration de l'entreprise
* Génération de bulletins de paie PDF

---

## 🚀 Fonctionnalités

### 👨‍💼 Gestion des employés

* Ajout d'employés
* Modification des informations
* Suppression d'employés
* Recherche rapide
* Filtrage par poste
* Filtrage par type de contrat

### ⏱ Gestion des présences

* Pointage des employés
* Gestion des retards
* Gestion des absences
* Détection des départs anticipés
* Calcul des heures travaillées
* Calcul des heures supplémentaires

### 💰 Gestion des salaires

* Calcul automatique des salaires
* Gestion des bonus
* Gestion des déductions
* Calcul du salaire net
* Historique des paiements

### 🏖 Gestion des congés

* Congés payés
* Congés non payés
* Suivi des soldes de congés

### 💳 Gestion des avances

* Demande d'avance
* Validation des avances
* Déduction automatique lors de la paie

### 📊 Tableau de bord

Affichage en temps réel :

* Nombre total d'employés
* Masse salariale
* Salaire moyen
* Total payé
* Présences
* Retards
* Absences
* Activités récentes

### 🔒 Sécurité

* Authentification utilisateur
* Hachage des mots de passe
* Gestion des rôles
* Journalisation des actions

### 📝 Audit

Toutes les opérations importantes sont enregistrées :

* Ajout
* Modification
* Suppression
* Connexion
* Déconnexion

---

## 🛠 Technologies utilisées

### Backend

* Python 3.11+

### Interface graphique

* PySide6 (Qt6)

### Base de données

* SQLite3

### Rapports PDF

* ReportLab

### Graphiques

* Matplotlib

---

## 📂 Structure du projet

```text
Gestion-Salaire/
│
├── main.py
│
├── configuration/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   └── audit_model.py
│
├── modules/
│   ├── auth/
│   ├── dashboard/
│   ├── employes/
│   ├── presence/
│   ├── salaire/
│   ├── conges/
│   └── configuration/
│
├── resources/
│   ├── icons/
│   ├── images/
│   └── styles/
│
├── reports/
│
├── data/
│   └── gestion_salaire.db
│
└── README.md
```

---

## ⚙️ Installation

### 1. Cloner le projet

```bash
git clone https://github.com/votre-compte/gestion-salaire.git
cd gestion-salaire
```

### 2. Créer un environnement virtuel

Linux :

```bash
python3 -m venv cyber
source cyber/bin/activate
```

Windows :

```bash
python -m venv cyber
cyber\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

ou

```bash
pip install PySide6 matplotlib reportlab pandas openpyxl
```

---

## ▶️ Lancer l'application

```bash
python main.py
```

---

## 👤 Compte administrateur par défaut

```text
Nom d'utilisateur : admin
Mot de passe      : admin123
```

⚠️ Il est recommandé de modifier ce mot de passe lors de la première connexion.

---

## 📊 Base de données

La base SQLite est créée automatiquement :

```text
data/gestion_salaire.db
```

Tables principales :

* utilisateur
* employes
* presence
* salaire
* avances
* conges
* activite
* audit_log
* configuration

---

## 📄 Export PDF

L'application permet :

* Génération de bulletins de paie
* Export PDF des rapports RH
* Export des statistiques

---

## 🔐 Audit et Traçabilité

Chaque action effectuée dans l'application est enregistrée :

* utilisateur
* date
* module
* action
* ancienne valeur
* nouvelle valeur

afin de garantir la traçabilité complète des opérations.

---

## 🎯 Objectifs du projet

Ce projet a été développé afin de :

* Automatiser la gestion RH
* Réduire les erreurs de calcul de paie
* Centraliser les informations des employés
* Produire des statistiques RH fiables
* Faciliter le suivi administratif

---

## 👨‍💻 Auteur

Angelos Fifaliana

Projet académique et professionnel de gestion des ressources humaines et de la paie.

Version : 1.0.0
Année : 2026

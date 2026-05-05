import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "..", "data", "gestion_salaire.db")
DB_PATH = os.path.abspath(DB_PATH)
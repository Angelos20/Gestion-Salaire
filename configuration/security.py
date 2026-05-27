import hashlib
import os

# ─────────────────────────────
# 🔐 PASSWORD SECURITY
# ─────────────────────────────

def hash_password(password: str) -> str:
    """
    Hash sécurisé avec PBKDF2 + salt
    Format stocké: salt:hash (hex)
    """
    salt = os.urandom(16)

    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        100000
    )

    return f"{salt.hex()}:{hashed.hex()}"


def verify_password(password: str, stored_password: str) -> bool:
    """
    Vérifie un mot de passe contre un hash stocké
    """
    try:
        salt_hex, hash_hex = stored_password.split(":")
        salt = bytes.fromhex(salt_hex)

        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )

        return new_hash.hex() == hash_hex

    except Exception:
        return False


# ─────────────────────────────
# 👤 SESSION UTILISATEUR
# ─────────────────────────────

CURRENT_USER = None


def set_user(user_tuple):

    global CURRENT_USER

    if not user_tuple:
        CURRENT_USER = None
        return

    CURRENT_USER = {
        "id": user_tuple[0],
        "username": user_tuple[1],
        "email": user_tuple[2],
        "role": user_tuple[3]
    }

def get_user():
    """Retourne l'utilisateur connecté"""
    return CURRENT_USER


def logout():
    """Déconnecte l'utilisateur"""
    global CURRENT_USER
    CURRENT_USER = None


def is_authenticated() -> bool:
    """Vérifie si un utilisateur est connecté"""
    return CURRENT_USER is not None


# ─────────────────────────────
# 🧠 HELPERS
# ─────────────────────────────

def get_username() -> str:
    user = get_user()

    if not user:
        return "unknown"

    # admin reste admin
    if user.get("role") == "admin":
        return "admin"

    # autres utilisateurs → vrai nom
    return user.get("username", "unknown")

def get_user_id():
    """Retourne l'ID utilisateur"""
    user = get_user()
    return user.get("id") if user else None


def get_user_role():
    """Retourne le rôle utilisateur"""
    user = get_user()
    return user.get("role", "user") if user else "user"


def has_role(role: str) -> bool:
    """Vérifie le rôle"""
    user = get_user()
    return bool(user and user.get("role") == role)
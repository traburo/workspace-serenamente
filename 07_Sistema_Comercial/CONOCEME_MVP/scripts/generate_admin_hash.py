from getpass import getpass

from werkzeug.security import generate_password_hash


password = getpass("Nueva contraseña administrativa: ")
confirmation = getpass("Repite la contraseña: ")
if len(password) < 12:
    raise SystemExit("La contraseña debe tener al menos 12 caracteres.")
if password != confirmation:
    raise SystemExit("Las contraseñas no coinciden.")
print(generate_password_hash(password))

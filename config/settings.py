import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    # Corriendo como .exe (PyInstaller): la base de datos debe vivir JUNTO al
    # ejecutable. __file__ apunta a una carpeta temporal que se borra al cerrar.
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

# Se puede cambiar con la variable de entorno CRUD_DB (los tests la usan
# para trabajar con una base temporal y nunca tocar la real).
DB_PATH = Path(os.environ.get("CRUD_DB", BASE_DIR / "productos.db"))
DB_URL = f"sqlite:///{DB_PATH}"

# Apps cuyos modelos se cargan al crear las tablas.
INSTALLED_APPS = ["apps.shop"]

APP_NAME = os.environ.get("APP_NAME", "Tienda Tonito")
WINDOW_SIZE = os.environ.get("WINDOW_SIZE", (900, 500))
GENERAL_ERROR = "__general__"

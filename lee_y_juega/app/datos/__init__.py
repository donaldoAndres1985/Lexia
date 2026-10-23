"""
Módulo de acceso a datos y persistencia SQLite.
"""
from .modelos import Base, SesionLectura, TestResultado, RegistroTiempo, HistorialNivel, LeccionProgreso
from .repositorio import RepositorioDatos

__all__ = [
    "Base",
    "SesionLectura",
    "TestResultado",
    "RegistroTiempo",
    "HistorialNivel",
    "LeccionProgreso",
    "RepositorioDatos",
]

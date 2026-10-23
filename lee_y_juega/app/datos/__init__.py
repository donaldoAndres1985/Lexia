"""
Módulo de acceso a datos y persistencia SQLite.
"""
from .modelos import (
    Base,
    HistorialNivel,
    LeccionProgreso,
    Logro,
    MascotaEstado,
    RegistroTiempo,
    SesionLectura,
    SimulacroResultado,
    TestResultado,
)
from .repositorio import RepositorioDatos

__all__ = [
    "Base",
    "SesionLectura",
    "TestResultado",
    "RegistroTiempo",
    "HistorialNivel",
    "LeccionProgreso",
    "Logro",
    "MascotaEstado",
    "SimulacroResultado",
    "RepositorioDatos",
]

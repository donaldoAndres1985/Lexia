"""
Módulo de lectura, textos discontinuos, generación de preguntas y calificación.
"""
from .fuentes import GestorFuentesLectura, TipoTexto
from .seleccion import SelectorLectura
from .limpieza import FiltroAdecuacionYLimpieza
from .discontinuos import GeneradorTextosDiscontinuos
from .generador_preguntas import GeneradorPreguntas
from .calificacion import EvaluadorTest
from .dificultad import GestorDificultadAdaptativa

__all__ = [
    "GestorFuentesLectura",
    "TipoTexto",
    "SelectorLectura",
    "FiltroAdecuacionYLimpieza",
    "GeneradorTextosDiscontinuos",
    "GeneradorPreguntas",
    "EvaluadorTest",
    "GestorDificultadAdaptativa",
]

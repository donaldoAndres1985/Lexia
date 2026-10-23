"""
Gestor de dificultad adaptativa (Niveles 1 a 6).
Monitorea rachas de rendimiento y ajusta automáticamente la complejidad.
"""
from __future__ import annotations

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class GestorDificultadAdaptativa:
    """Controla el ascenso o descenso de nivel según el desempeño del estudiante."""

    NIVEL_MINIMO = 1
    NIVEL_MAXIMO = 6

    def __init__(self, repositorio, configuracion):
        self.repo = repositorio
        self.config = configuracion

    def verificar_y_actualizar_nivel(self) -> Tuple[int, Optional[str]]:
        """
        Revisa los últimos tests en la base de datos y determina si corresponde
        subir, bajar o mantener el nivel actual.
        Retorna (nivel_actualizado, mensaje_notificacion).
        """
        nivel_actual = self.repo.obtener_nivel_actual()
        consecutivos_subir = int(self.config.obtener("subir_nivel_consecutivos", 3))
        min_puntaje_subir = float(self.config.obtener("subir_nivel_min_puntaje", 85.0))
        consecutivos_bajar = int(self.config.obtener("bajar_nivel_consecutivos", 2))

        ultimos_tests = self.repo.obtener_ultimos_tests(limite=max(consecutivos_subir, consecutivos_bajar))
        if not ultimos_tests:
            return nivel_actual, None

        # 1. Evaluar si sube de nivel
        if len(ultimos_tests) >= consecutivos_subir and nivel_actual < self.NIVEL_MAXIMO:
            sube = all(
                t.aprobado and t.puntaje_porcentaje >= min_puntaje_subir
                for t in ultimos_tests[:consecutivos_subir]
            )
            if sube:
                nuevo_nivel = nivel_actual + 1
                razon = f"{consecutivos_subir} tests consecutivos aprobados con puntaje ≥ {min_puntaje_subir}%"
                self.repo.registrar_cambio_nivel(nuevo_nivel, razon)
                mensaje = f"¡Felicidades! Has demostrado una comprensión sobresaliente y subiste al Nivel {nuevo_nivel}."
                return nuevo_nivel, mensaje

        # 2. Evaluar si baja de nivel (para no frustrar a la estudiante)
        if len(ultimos_tests) >= consecutivos_bajar and nivel_actual > self.NIVEL_MINIMO:
            baja = all(not t.aprobado for t in ultimos_tests[:consecutivos_bajar])
            if baja:
                nuevo_nivel = nivel_actual - 1
                razon = f"{consecutivos_bajar} tests consecutivos reprobados"
                self.repo.registrar_cambio_nivel(nuevo_nivel, razon)
                mensaje = f"Ajustamos la dificultad al Nivel {nuevo_nivel} para repasar con textos más amigables. ¡Tú puedes!"
                return nuevo_nivel, mensaje

        return nivel_actual, None

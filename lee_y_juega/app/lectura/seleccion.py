"""
Selección inteligente y rotativa de lecturas.
Alterna tipos de texto (literario, informativo, discontinuo)
y evita repeticiones recientes.
"""
from __future__ import annotations

import logging
import random
from typing import Any, Dict, List, Optional

from .fuentes import GestorFuentesLectura, TipoTexto

logger = logging.getLogger(__name__)


class SelectorLectura:
    """Selecciona lecturas equilibrando tipos de texto, nivel y variedad."""

    def __init__(self, gestor_fuentes: GestorFuentesLectura):
        self.fuentes = gestor_fuentes
        self.historial_recientes: List[str] = []
        self._ultimo_tipo_texto: Optional[str] = None

    def proximo_tipo_texto_sugerido(self) -> str:
        """Alterna cíclicamente: Literario -> Informativo -> Discontinuo -> Literario."""
        secuencia = [
            TipoTexto.LITERARIO.value,
            TipoTexto.INFORMATIVO.value,
            TipoTexto.DISCONTINUO.value,
        ]
        if not self._ultimo_tipo_texto or self._ultimo_tipo_texto not in secuencia:
            return TipoTexto.LITERARIO.value

        idx = secuencia.index(self._ultimo_tipo_texto)
        siguiente = secuencia[(idx + 1) % len(secuencia)]
        return siguiente

    def seleccionar_lectura(
        self,
        nivel: int,
        tipo_forzado: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Selecciona la mejor lectura para la sesión actual según el nivel y la rotación.
        """
        tipo_objetivo = tipo_forzado or self.proximo_tipo_texto_sugerido()
        self._ultimo_tipo_texto = tipo_objetivo

        # Si el tipo es discontinuo y queremos gráfico generado con Matplotlib
        if tipo_objetivo == TipoTexto.DISCONTINUO.value and random.random() < 0.5:
            logger.info("Generando texto discontinuo dinámico con Matplotlib.")
            subtipo = "tabla" if random.random() < 0.5 else "barras"
            return self.fuentes.obtener_texto_discontinuo_generado(subtipo)

        candidatas = [
            l for l in self.fuentes.lecturas_offline
            if l.get("tipo_texto") == tipo_objetivo
            and l.get("id") not in self.historial_recientes
        ]

        # Si no hay del tipo objetivo no leídas, considerar cualquier tipo no leído
        if not candidatas:
            candidatas = [
                l for l in self.fuentes.lecturas_offline
                if l.get("id") not in self.historial_recientes
            ]

        # Si ya se leyeron todas, reiniciar historial reciente
        if not candidatas:
            self.historial_recientes.clear()
            candidatas = self.fuentes.lecturas_offline

        # Filtrar o priorizar por cercanía al nivel
        candidatas_nivel = [c for c in candidatas if abs(c.get("nivel", 1) - nivel) <= 1]
        seleccion = random.choice(candidatas_nivel if candidatas_nivel else candidatas)

        self.historial_recientes.append(seleccion["id"])
        # Mantener historial acotado a las últimas 15
        if len(self.historial_recientes) > 15:
            self.historial_recientes.pop(0)

        logger.info(f"Lectura seleccionada: {seleccion.get('titulo')} (Nivel {seleccion.get('nivel')})")
        return seleccion

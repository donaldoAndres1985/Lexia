"""
Controlador de bloqueo kiosco.
Coordina entre el monitor de actividad, el banco de tiempo y la ventana kiosco.
"""
from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal

from .banco_tiempo import BancoTiempo
from .monitor_actividad import CategoriaActividad, MonitorActividad

logger = logging.getLogger(__name__)


class ControladorBloqueo(QObject):
    """
    Supervisa las condiciones de bloqueo y solicita mostrar
    o cerrar la ventana de bloqueo tipo kiosco.
    """
    solicitar_bloqueo = Signal(str)    # Mensaje o motivo del bloqueo
    solicitar_desbloqueo = Signal()    # Cierre del kiosco

    def __init__(
        self,
        monitor: MonitorActividad,
        banco: BancoTiempo,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.monitor = monitor
        self.banco = banco
        self.bloqueo_activo = False

        # Conectar señales
        self.monitor.actividad_cambiada.connect(self._al_cambiar_actividad)
        self.banco.tiempo_agotado.connect(self._al_agotar_tiempo)
        self.banco.fuera_de_horario.connect(self._al_fuera_de_horario)

    def _al_cambiar_actividad(self, categoria: str, proceso: str, titulo: str) -> None:
        """Si la actividad pasa a ser ocio y no hay saldo de tiempo, bloquea de inmediato."""
        self.banco.establecer_actividad(categoria)
        
        if categoria == CategoriaActividad.OCIO.value:
            if self.banco.minutos_disponibles <= 0 or not self.banco.esta_en_horario_permitido():
                if not self.bloqueo_activo:
                    motivo = "¡Tu tiempo de ocio terminó! Lee y aprueba el test para ganar más minutos."
                    self.activar_bloqueo(motivo)

    def _al_agotar_tiempo(self) -> None:
        if not self.bloqueo_activo and self.banco.categoria_actual == CategoriaActividad.OCIO:
            self.activar_bloqueo("¡Se acabó el tiempo de juego! Vamos a leer un poco.")

    def _al_fuera_de_horario(self, mensaje: str) -> None:
        if not self.bloqueo_activo and self.banco.categoria_actual == CategoriaActividad.OCIO:
            self.activar_bloqueo(mensaje)

    def activar_bloqueo(self, motivo: str = "") -> None:
        """Activa la pantalla kiosco."""
        self.bloqueo_activo = True
        self.banco.kiosco_activo = True
        logger.info(f"Activando bloqueo kiosco: {motivo}")
        self.solicitar_bloqueo.emit(motivo)

    def desactivar_bloqueo(self) -> None:
        """Desactiva la pantalla kiosco (por test aprobado o clave de padre)."""
        self.bloqueo_activo = False
        self.banco.kiosco_activo = False
        logger.info("Desactivando bloqueo kiosco.")
        self.solicitar_desbloqueo.emit()

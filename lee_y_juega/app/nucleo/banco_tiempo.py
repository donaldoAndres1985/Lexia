"""
Gestión del banco de tiempo de ocio.
Controla el consumo según actividad, recompensas y horarios permitidos.
"""
from __future__ import annotations

import logging
from datetime import datetime, time
from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal

from .monitor_actividad import CategoriaActividad

logger = logging.getLogger(__name__)


class BancoTiempo(QObject):
    """
    Administra los minutos de ocio disponibles, descuenta tiempo
    durante actividades recreativas y emite avisos de agotamiento.
    """
    balance_actualizado = Signal(float)       # Nuevo balance en minutos
    tiempo_agotado = Signal()                 # Se llegó a 0 minutos de ocio
    fuera_de_horario = Signal(str)            # Notificación de horario restringido

    def __init__(self, repositorio, configuracion, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.repo = repositorio
        self.config = configuracion

        # Cargar balance inicial del día desde base de datos
        self.minutos_disponibles = self.repo.obtener_balance_actual()
        
        # Si es el primer uso del día y el padre configuró ocio inicial
        tiempo_inicial = float(self.config.obtener("tiempo_ocio_inicial_min", 0))
        if self.minutos_disponibles == 0 and tiempo_inicial > 0:
            self.minutos_disponibles = self.repo.sumar_minutos(tiempo_inicial)

        self.categoria_actual = CategoriaActividad.NEUTRO
        self.kiosco_activo = False

        # Temporizador de consumo (cada segundo para exactitud)
        self._timer_consumo = QTimer(self)
        self._timer_consumo.setInterval(1000)
        self._timer_consumo.timeout.connect(self._tick_consumo)
        self._timer_consumo.start()

    def establecer_actividad(self, categoria_str: str) -> None:
        """Actualiza la categoría de actividad reportada por el monitor."""
        try:
            self.categoria_actual = CategoriaActividad(categoria_str)
        except ValueError:
            self.categoria_actual = CategoriaActividad.NEUTRO

    def esta_en_horario_permitido(self) -> bool:
        """Comprueba si la hora actual está dentro del rango permitido para jugar."""
        try:
            h_inicio = self.config.obtener("horario_ocio_inicio", "08:00")
            h_fin = self.config.obtener("horario_ocio_fin", "21:00")
            
            t_inicio = datetime.strptime(h_inicio, "%H:%M").time()
            t_fin = datetime.strptime(h_fin, "%H:%M").time()
            ahora = datetime.now().time()

            if t_inicio <= t_fin:
                return t_inicio <= ahora <= t_fin
            else:
                # Caso que cruza la medianoche
                return ahora >= t_inicio or ahora <= t_fin
        except Exception as e:
            logger.error(f"Error al evaluar horario permitido: {e}")
            return True

    def agregar_recompensa_lectura(self) -> float:
        """Suma el tiempo configurado tras aprobar un test."""
        minutos = float(self.config.obtener("tiempo_recompensa_min", 60))
        self.minutos_disponibles = self.repo.sumar_minutos(minutos)
        self.balance_actualizado.emit(self.minutos_disponibles)
        logger.info(f"Recompensa otorgada: +{minutos} min. Total: {self.minutos_disponibles} min.")
        return self.minutos_disponibles

    def ajustar_manualmente(self, delta_minutos: float) -> float:
        """Modificación manual desde el modo padre."""
        self.minutos_disponibles = self.repo.ajustar_minutos_manual(delta_minutos)
        self.balance_actualizado.emit(self.minutos_disponibles)
        return self.minutos_disponibles

    def _tick_consumo(self) -> None:
        """Se ejecuta cada segundo. Descuenta tiempo si la actividad es OCIO."""
        if self.kiosco_activo:
            # Mientras la ventana kiosco esté abierta, no se descuenta tiempo
            return

        # Verificar restricción horaria
        if not self.esta_en_horario_permitido() and self.categoria_actual == CategoriaActividad.OCIO:
            self.fuera_de_horario.emit("Fuera del horario de ocio configurado.")
            self.tiempo_agotado.emit()
            return

        # Solo descuenta si está en OCIO
        if self.categoria_actual == CategoriaActividad.OCIO:
            delta_minutos = 1.0 / 60.0  # 1 segundo en minutos
            self.minutos_disponibles = max(0.0, self.minutos_disponibles - delta_minutos)
            
            # Guardar en base de datos cada 15 segundos para no sobrecargar SQLite
            if int(datetime.now().timestamp()) % 15 == 0:
                self.repo.descontar_minutos(15.0 / 60.0)

            self.balance_actualizado.emit(self.minutos_disponibles)

            if self.minutos_disponibles <= 0.0:
                logger.info("Tiempo de ocio agotado.")
                self.tiempo_agotado.emit()

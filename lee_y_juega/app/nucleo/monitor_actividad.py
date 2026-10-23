"""
Monitor de actividad de ventanas y procesos en Windows.
Clasifica la ventana en primer plano en OCIO, ESTUDIO o NEUTRO.
"""
from __future__ import annotations

import logging
import sys
from enum import Enum
from typing import Callable, Optional, Tuple

import psutil
from PySide6.QtCore import QObject, QTimer, Signal

logger = logging.getLogger(__name__)

# Intentar importar pywin32 para Windows
_HAVE_WIN32 = False
if sys.platform == "win32":
    try:
        import win32gui
        import win32process
        _HAVE_WIN32 = True
    except ImportError:
        logger.warning("pywin32 no disponible en este entorno.")


class CategoriaActividad(str, Enum):
    OCIO = "OCIO"
    ESTUDIO = "ESTUDIO"
    NEUTRO = "NEUTRO"


class MonitorActividad(QObject):
    """
    Sondea la ventana activa cada N segundos y emite señales
    con su clasificación y metadatos.
    """
    actividad_cambiada = Signal(str, str, str)  # (categoria, nombre_proceso, titulo_ventana)

    def __init__(self, configuracion, intervalo_segundos: float = 3.0, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.config = configuracion
        self.intervalo_ms = int(intervalo_segundos * 1000)
        
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._verificar_ventana_activa)
        
        self.ultima_categoria = CategoriaActividad.NEUTRO
        self.ultimo_proceso = ""
        self.ultimo_titulo = ""

    def iniciar(self) -> None:
        """Inicia el monitoreo periódico."""
        self._timer.start(self.intervalo_ms)
        self._verificar_ventana_activa()
        logger.info("Monitor de actividad iniciado.")

    def detener(self) -> None:
        """Detiene el monitoreo periódico."""
        self._timer.stop()
        logger.info("Monitor de actividad detenido.")

    def obtener_ventana_primer_plano(self) -> Tuple[str, str]:
        """
        Obtiene el proceso ejecutable y el título de la ventana activa.
        Retorna (nombre_proceso, titulo_ventana).
        """
        if not _HAVE_WIN32:
            return ("", "Simulación de ventana neutra")

        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return ("", "")
            
            titulo = win32gui.GetWindowText(hwnd) or ""
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            proceso_nombre = ""
            if pid > 0:
                try:
                    proc = psutil.Process(pid)
                    proceso_nombre = proc.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    proceso_nombre = ""
            
            return (proceso_nombre, titulo)
        except Exception as e:
            logger.debug(f"Error al obtener ventana en primer plano: {e}")
            return ("", "")

    def clasificar(self, proceso: str, titulo: str) -> CategoriaActividad:
        """
        Clasifica la actividad según las reglas de configuración:
        1. Reglas de ESTUDIO tienen prioridad para no perjudicar tareas escolares.
        2. Reglas de OCIO (procesos de juegos o títulos de redes/videos).
        3. NEUTRO si no coincide con ninguna.
        """
        if not proceso and not titulo:
            return CategoriaActividad.NEUTRO

        proceso_lower = proceso.lower()
        titulo_lower = titulo.lower()

        # 1. Verificar ESTUDIO
        apps_estudio = [a.lower() for a in self.config.obtener("apps_estudio", [])]
        titulos_estudio = [t.lower() for t in self.config.obtener("titulos_estudio", [])]

        if any(app in proceso_lower for app in apps_estudio if app):
            return CategoriaActividad.ESTUDIO

        if any(t in titulo_lower for t in titulos_estudio if t):
            return CategoriaActividad.ESTUDIO

        # 2. Verificar OCIO
        apps_ocio = [a.lower() for a in self.config.obtener("apps_ocio", [])]
        titulos_ocio = [t.lower() for t in self.config.obtener("titulos_ocio", [])]

        if any(app in proceso_lower for app in apps_ocio if app):
            return CategoriaActividad.OCIO

        if any(t in titulo_lower for t in titulos_ocio if t):
            return CategoriaActividad.OCIO

        # 3. Música permitida no cuenta como ocio si la ventana principal no es juego/video
        titulos_musica = [m.lower() for m in self.config.obtener("titulos_musica_permitida", [])]
        if any(m in titulo_lower for m in titulos_musica if m):
            return CategoriaActividad.NEUTRO

        return CategoriaActividad.NEUTRO

    def _verificar_ventana_activa(self) -> None:
        proceso, titulo = self.obtener_ventana_primer_plano()
        categoria = self.clasificar(proceso, titulo)
        
        # Guardar estado actual
        self.ultima_categoria = categoria
        self.ultimo_proceso = proceso
        self.ultimo_titulo = titulo

        # Emitir señal a los controladores
        self.actividad_cambiada.emit(categoria.value, proceso, titulo)

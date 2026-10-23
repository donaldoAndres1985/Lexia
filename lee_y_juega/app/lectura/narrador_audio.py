"""
Narrador de audio Text-to-Speech (TTS) para Lee y Juega.
Utiliza el motor nativo de síntesis de voz de Windows (SAPI5) a través de pywin32.
Funciona 100% offline, en un hilo seguro para no bloquear la interfaz gráfica.
"""
from __future__ import annotations

import logging
import re
import sys
from typing import Optional

from PySide6.QtCore import QObject, QThread, Signal

logger = logging.getLogger(__name__)

_HAVE_SAPI = False
if sys.platform == "win32":
    try:
        import win32com.client
        import pythoncom
        _HAVE_SAPI = True
    except ImportError:
        logger.warning("win32com no disponible para SAPI5 TTS.")


class HiloNarracion(QThread):
    """Hilo secundario que reproduce la voz sintética."""
    terminado = Signal()
    error_ocurrido = Signal(str)

    def __init__(self, texto: str, velocidad: int = 0, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.texto = texto
        self.velocidad = velocidad
        self._detener_solicitado = False

    def run(self) -> None:
        if not _HAVE_SAPI:
            self.error_ocurrido.emit("Síntesis de voz no disponible en este sistema.")
            return

        try:
            import pythoncom
            pythoncom.CoInitialize()

            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Rate = self.velocidad  # -10 a 10 (0 normal)

            # Buscar voz en español si está disponible en Windows
            voices = speaker.GetVoices()
            for v in voices:
                desc = v.GetDescription().lower()
                if "spanish" in desc or "español" in desc or "sabina" in desc or "helena" in desc or "mexico" in desc:
                    speaker.Voice = v
                    break

            # Limpiar texto de formato o etiquetas
            texto_limpio = re.sub(r"<[^>]+>", "", self.texto)
            texto_limpio = re.sub(r"\[\d+\]", "", texto_limpio)

            # Reproducir sincrónicamente en este hilo de fondo
            speaker.Speak(texto_limpio)
            pythoncom.CoUninitialize()
            self.terminado.emit()
        except Exception as e:
            logger.error(f"Error en narrador de voz: {e}")
            self.error_ocurrido.emit(str(e))

    def detener(self) -> None:
        self._detener_solicitado = True
        self.terminate()


class NarradorAudio(QObject):
    """Controlador de lectura en voz alta para la interfaz de usuario."""
    estado_cambiado = Signal(bool)  # True = narrando, False = detenido

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._hilo_actual: Optional[HiloNarracion] = None
        self.narrando = False

    def reproducir(self, texto: str) -> None:
        """Inicia la lectura en voz alta."""
        self.detener()
        self._hilo_actual = HiloNarracion(texto, velocidad=-1, parent=self)
        self._hilo_actual.terminado.connect(self._al_terminar)
        self._hilo_actual.error_ocurrido.connect(self._al_error)
        self.narrando = True
        self.estado_cambiado.emit(True)
        self._hilo_actual.start()

    def detener(self) -> None:
        """Detiene inmediatamente la narración."""
        if self._hilo_actual and self._hilo_actual.isRunning():
            self._hilo_actual.detener()
            self._hilo_actual.wait(500)
            self._hilo_actual = None
        self.narrando = False
        self.estado_cambiado.emit(False)

    def alternar(self, texto: str) -> bool:
        """Alterna entre reproducir y detener. Retorna el nuevo estado."""
        if self.narrando:
            self.detener()
            return False
        else:
            self.reproducir(texto)
            return True

    def _al_terminar(self) -> None:
        self.narrando = False
        self.estado_cambiado.emit(False)

    def _al_error(self, err: str) -> None:
        self.narrando = False
        self.estado_cambiado.emit(False)

"""
Icono en la bandeja del sistema (System Tray) para Lee y Juega.
Muestra el tiempo restante disponible y acceso al menú contextual.
"""
from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

logger = logging.getLogger(__name__)


class BandejaSistema(QObject):
    """Administra el icono de la bandeja y sus opciones contextuales."""

    solicitar_modo_padre = Signal()
    solicitar_lecciones = Signal()
    solicitar_salir = Signal()

    def __init__(self, banco_tiempo, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.banco = banco_tiempo

        self.tray = QSystemTrayIcon(self)
        self.menu = QMenu()

        self._construir_menu()
        self.actualizar_tiempo(self.banco.minutos_disponibles)

        # Conectar señal de actualización del banco
        self.banco.balance_actualizado.connect(self.actualizar_tiempo)

    def iniciar(self) -> None:
        self.tray.show()
        logger.info("Icono de bandeja iniciado.")

    def ocultar(self) -> None:
        self.tray.hide()

    def _construir_menu(self) -> None:
        self.accion_tiempo = QAction("⏱️ Tiempo: Calculando...", self.menu)
        self.accion_tiempo.setEnabled(False)
        self.menu.addAction(self.accion_tiempo)

        self.menu.addSeparator()

        accion_aprender = QAction("📚 Menú Aprender (Lecciones)", self.menu)
        accion_aprender.triggered.connect(self.solicitar_lecciones.emit)
        self.menu.addAction(accion_aprender)

        accion_padre = QAction("🔐 Modo Padre (Configuración)", self.menu)
        accion_padre.triggered.connect(self.solicitar_modo_padre.emit)
        self.menu.addAction(accion_padre)

        self.menu.addSeparator()

        accion_salir = QAction("❌ Salir de Lee y Juega", self.menu)
        accion_salir.triggered.connect(self.solicitar_salir.emit)
        self.menu.addAction(accion_salir)

        self.tray.setContextMenu(self.menu)

    def actualizar_tiempo(self, minutos: float) -> None:
        """Actualiza el texto del menú, tooltip e ícono con los minutos restantes."""
        minutos_redondeados = max(0, int(minutos))
        texto_tiempo = f"⏱️ Tiempo disponible: {minutos_redondeados} min"
        self.accion_tiempo.setText(texto_tiempo)
        self.tray.setToolTip(f"Lee y Juega — {minutos_redondeados} min de ocio disponibles")

        # Generar icono con el número
        icono = self._crear_icono_tiempo(minutos_redondeados)
        self.tray.setIcon(icono)

    @staticmethod
    def _crear_icono_tiempo(minutos: int) -> QIcon:
        """Dibuja un icono dinámico con un círculo y los minutos restantes."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparente

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Color según estado
        if minutos > 15:
            color_fondo = QColor("#10B981")  # Verde
        elif minutos > 5:
            color_fondo = QColor("#F59E0B")  # Ámbar
        else:
            color_fondo = QColor("#EF4444")  # Rojo

        # Círculo
        painter.setBrush(color_fondo)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawEllipse(1, 1, 30, 30)

        # Texto del número
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Arial", 11, QFont.Bold)
        painter.setFont(font)

        texto = str(min(minutos, 99))
        painter.drawText(pixmap.rect(), 0x0084, texto)  # Qt.AlignCenter
        painter.end()

        return QIcon(pixmap)

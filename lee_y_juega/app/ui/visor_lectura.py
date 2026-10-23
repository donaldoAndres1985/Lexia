"""
Visor interactivo de lectura con subrayador y diccionario al doble clic.
Permite lectura activa mediante resaltado de colores y modos visuales (Blanco, Sepia, Noche).
"""
from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QTextEdit, QWidget

logger = logging.getLogger(__name__)


class VisorLecturaInteractiva(QTextEdit):
    """Área de lectura enriquecida para 7.º grado con herramientas de estudio."""

    palabra_consultada = Signal(str)  # Emitida al hacer doble clic en una palabra

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setStyleSheet("""
            QTextEdit {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 17px;
                line-height: 1.6;
                color: #1E293B;
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 16px;
            }
        """)

    def mouseDoubleClickEvent(self, event) -> None:
        """Al hacer doble clic sobre una palabra, emite la señal para el diccionario contextual."""
        super().mouseDoubleClickEvent(event)
        cursor = self.textCursor()
        palabra = cursor.selectedText().strip()
        if palabra and len(palabra) > 2 and palabra.isalpha():
            self.palabra_consultada.emit(palabra)

    def resaltar_seleccion(self, color_hex: str) -> None:
        """Aplica fondo de color al texto seleccionado actualmente con el mouse."""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return

        formato = QTextCharFormat()
        if color_hex == "limpiar":
            formato.setBackground(QColor(0, 0, 0, 0))  # Transparente
        else:
            formato.setBackground(QColor(color_hex))

        cursor.mergeCharFormat(formato)

    def aplicar_modo_visual(self, modo: str) -> None:
        """Cambia el esquema de colores para comodidad de lectura."""
        if modo == "sepia":
            self.setStyleSheet("""
                QTextEdit {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 17px;
                    line-height: 1.6;
                    color: #4A3B32;
                    background-color: #FBF0D9;
                    border: 1px solid #E8D8B8;
                    border-radius: 10px;
                    padding: 16px;
                }
            """)
        elif modo == "noche":
            self.setStyleSheet("""
                QTextEdit {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 17px;
                    line-height: 1.6;
                    color: #E2E8F0;
                    background-color: #1E293B;
                    border: 1px solid #334155;
                    border-radius: 10px;
                    padding: 16px;
                }
            """)
        else:  # Blanco estándar
            self.setStyleSheet("""
                QTextEdit {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 17px;
                    line-height: 1.6;
                    color: #1E293B;
                    background-color: #FFFFFF;
                    border: 1px solid #E2E8F0;
                    border-radius: 10px;
                    padding: 16px;
                }
            """)

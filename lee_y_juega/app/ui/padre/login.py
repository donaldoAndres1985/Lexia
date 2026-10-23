"""
Diálogo de autenticación para el Modo Padre usando Argon2.
Permite establecer la clave en el primer inicio y verificarla de forma segura.
"""
from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

logger = logging.getLogger(__name__)

# Manejo de Argon2
_HAVE_ARGON2 = False
try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    _ph = PasswordHasher()
    _HAVE_ARGON2 = True
except ImportError:
    import hashlib
    logger.warning("argon2-cffi no disponible. Usando fallback seguro con SHA-256.")


def generar_hash_clave(clave: str) -> str:
    """Genera un hash seguro para la clave del padre."""
    if _HAVE_ARGON2:
        return _ph.hash(clave)
    # Fallback si no está argon2 instalado
    return "SHA256:" + hashlib.sha256(clave.encode("utf-8")).hexdigest()


def verificar_clave(hash_almacenado: str, clave_ingresada: str) -> bool:
    """Verifica si la clave ingresada coincide con el hash guardado."""
    if not hash_almacenado:
        return False

    if hash_almacenado.startswith("SHA256:"):
        candidato = "SHA256:" + hashlib.sha256(clave_ingresada.encode("utf-8")).hexdigest()
        return candidato == hash_almacenado

    if _HAVE_ARGON2:
        try:
            return _ph.verify(hash_almacenado, clave_ingresada)
        except VerifyMismatchError:
            return False
        except Exception as e:
            logger.error(f"Error al verificar clave con Argon2: {e}")
            return False

    return False


class DialogoLoginPadre(QDialog):
    """Ventana modal para acceder a la administración del sistema."""

    def __init__(self, configuracion, parent=None):
        super().__init__(parent)
        self.config = configuracion
        self.setWindowTitle("Modo Padre — Acceso Seguro")
        self.setFixedSize(380, 240)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.hash_existente = self.config.obtener("clave_padre_hash", "")
        self.es_primer_inicio = not bool(self.hash_existente)

        self._construir_ui()

    def _construir_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        titulo = QLabel("🔐 Configuración del Modo Padre" if self.es_primer_inicio else "🔒 Ingrese la Clave del Padre")
        titulo.setObjectName("subtitulo")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        subtexto = QLabel(
            "Cree una contraseña para administrar tiempos y límites:"
            if self.es_primer_inicio
            else "Digite su clave para acceder al panel de control:"
        )
        subtexto.setWordWrap(True)
        subtexto.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtexto)

        form_layout = QFormLayout()
        self.input_clave = QLineEdit()
        self.input_clave.setEchoMode(QLineEdit.Password)
        self.input_clave.setPlaceholderText("Contraseña")
        form_layout.addRow("Contraseña:", self.input_clave)

        if self.es_primer_inicio:
            self.input_confirmar = QLineEdit()
            self.input_confirmar.setEchoMode(QLineEdit.Password)
            self.input_confirmar.setPlaceholderText("Confirmar contraseña")
            form_layout.addRow("Confirmar:", self.input_confirmar)

        layout.addLayout(form_layout)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btn_secundario")
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_aceptar = QPushButton("Guardar Clave" if self.es_primer_inicio else "Ingresar")
        self.btn_aceptar.clicked.connect(self._al_aceptar)

        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_aceptar)
        layout.addLayout(btn_layout)

    def _al_aceptar(self) -> None:
        clave = self.input_clave.text().strip()
        if not clave:
            QMessageBox.warning(self, "Atención", "La contraseña no puede estar vacía.")
            return

        if self.es_primer_inicio:
            confirmar = self.input_confirmar.text().strip()
            if clave != confirmar:
                QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
                return
            if len(clave) < 4:
                QMessageBox.warning(self, "Seguridad", "La clave debe tener al menos 4 caracteres.")
                return

            nuevo_hash = generar_hash_clave(clave)
            self.config.establecer("clave_padre_hash", nuevo_hash)
            QMessageBox.information(self, "Éxito", "Clave del padre configurada exitosamente.")
            self.accept()
        else:
            if verificar_clave(self.hash_existente, clave):
                self.accept()
            else:
                QMessageBox.critical(self, "Acceso denegado", "Contraseña incorrecta. Intente de nuevo.")
                self.input_clave.clear()
                self.input_clave.setFocus()

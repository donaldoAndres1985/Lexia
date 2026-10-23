"""
Componentes lúdicos e interactivos de la interfaz:
- Widget y diálogo de Koko el Colibrí (mascota virtual)
- Galería de Medallas e Insignias desbloqueables (Logros)
- Tarjeta emergente de Diccionario Contextual
- Ruleta animada de Bonificación Extra por puntaje 100%
"""
from __future__ import annotations

import logging
import random
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QPoint, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..lectura.diccionario import GlosarioContextual

logger = logging.getLogger(__name__)


class WidgetMascota(QFrame):
    """Muestra el avatar de Koko el Colibrí con su nivel, barra de XP y globo de diálogo."""

    def __init__(self, repositorio, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.repo = repositorio
        self.setObjectName("tarjeta")
        self.setFixedHeight(95)
        self.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0;")
        self._construir_ui()
        self.actualizar_datos()

    def _construir_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Avatar gráfico de Koko
        self.lbl_avatar = QLabel("🦉")
        self.lbl_avatar.setStyleSheet("font-size: 38px;")
        layout.addWidget(self.lbl_avatar)

        # Datos de nivel y diálogo
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)

        cabecera = QHBoxLayout()
        self.lbl_nombre = QLabel("Koko el Colibrí Sabio")
        self.lbl_nombre.setStyleSheet("font-weight: bold; font-size: 13px; color: #4F46E5;")
        self.lbl_nivel = QLabel("Nv. 1")
        self.lbl_nivel.setStyleSheet("background-color: #EEF2FF; color: #4338CA; font-weight: bold; font-size: 11px; padding: 2px 6px; border-radius: 4px;")
        cabecera.addWidget(self.lbl_nombre)
        cabecera.addWidget(self.lbl_nivel)
        cabecera.addStretch()
        info_layout.addLayout(cabecera)

        # Globo de texto de ánimo
        self.lbl_globo = QLabel("¡Hola! Vamos a leer juntos.")
        self.lbl_globo.setStyleSheet("font-size: 12px; color: #334155; font-style: italic;")
        self.lbl_globo.setWordWrap(True)
        info_layout.addWidget(self.lbl_globo)

        # Barra de experiencia pequeña
        self.barra_xp = QProgressBar()
        self.barra_xp.setFixedHeight(6)
        self.barra_xp.setTextVisible(False)
        self.barra_xp.setStyleSheet("QProgressBar::chunk { background-color: #10B981; border-radius: 3px; }")
        info_layout.addWidget(self.barra_xp)

        layout.addLayout(info_layout)

    def actualizar_datos(self) -> None:
        datos = self.repo.obtener_estado_mascota()
        self.lbl_nombre.setText(datos["nombre"])
        self.lbl_nivel.setText(f"Nv. {datos['nivel']}")
        self.lbl_globo.setText(f"«{datos['frase_actual']}»")

        xp_actual = datos["experiencia"]
        xp_max = datos["xp_siguiente_nivel"]
        self.barra_xp.setMaximum(xp_max)
        self.barra_xp.setValue(xp_actual)

        # Cambiar icono según nivel
        iconos = {1: "🦉", 2: "🪶", 3: "🦅", 4: "🦜", 5: "👑"}
        self.lbl_avatar.setText(iconos.get(datos["nivel"], "🌟"))


class DialogoLogros(QDialog):
    """Muestra la galería de medallas e insignias ganadas."""

    def __init__(self, repositorio, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.repo = repositorio
        self.setWindowTitle("🏆 Mis Medallas y Logros de Lectura")
        self.resize(650, 480)
        self._construir_ui()

    def _construir_ui(self) -> None:
        layout = QVBoxLayout(self)

        encabezado = QLabel("Tus Medallas de Mérito Lector")
        encabezado.setObjectName("titulo_grande")
        encabezado.setAlignment(Qt.AlignCenter)
        layout.addWidget(encabezado)

        subtexto = QLabel("Cada medalla representa tu dedicación y agudeza para comprender textos.")
        subtexto.setAlignment(Qt.AlignCenter)
        subtexto.setStyleSheet("color: #64748B; font-size: 13px; margin-bottom: 10px;")
        layout.addWidget(subtexto)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        contenedor = QWidget()
        grid = QGridLayout(contenedor)
        grid.setSpacing(12)

        logros = self.repo.obtener_logros()
        for i, l in enumerate(logros):
            caja = QFrame()
            desbloqueado = l["desbloqueado"]
            bg = "#ECFDF5" if desbloqueado else "#F1F5F9"
            border = "#10B981" if desbloqueado else "#CBD5E1"
            caja.setStyleSheet(f"background-color: {bg}; border: 1.5px solid {border}; border-radius: 10px; padding: 10px;")

            l_box = QVBoxLayout(caja)
            l_box.setSpacing(4)

            ico = l["icono"] if desbloqueado else "🔒"
            lbl_ico = QLabel(ico)
            lbl_ico.setStyleSheet("font-size: 26px;")
            lbl_ico.setAlignment(Qt.AlignCenter)

            lbl_nom = QLabel(l["nombre"])
            lbl_nom.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E293B;")
            lbl_nom.setAlignment(Qt.AlignCenter)

            lbl_desc = QLabel(l["descripcion"])
            lbl_desc.setWordWrap(True)
            lbl_desc.setStyleSheet("font-size: 11px; color: #475569;")
            lbl_desc.setAlignment(Qt.AlignCenter)

            l_box.addWidget(lbl_ico)
            l_box.addWidget(lbl_nom)
            l_box.addWidget(lbl_desc)

            if desbloqueado and l["fecha_desbloqueo"]:
                lbl_fecha = QLabel(f"Conseguida: {l['fecha_desbloqueo']}")
                lbl_fecha.setStyleSheet("font-size: 10px; color: #059669; font-weight: bold;")
                lbl_fecha.setAlignment(Qt.AlignCenter)
                l_box.addWidget(lbl_fecha)

            grid.addWidget(caja, i // 2, i % 2)

        scroll.setWidget(contenedor)
        layout.addWidget(scroll)

        btn_cerrar = QPushButton("¡Genial! Seguir Leyendo")
        btn_cerrar.setFixedHeight(40)
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)


class DialogoDiccionario(QDialog):
    """Ventana emergente que define una palabra al hacer doble clic."""

    def __init__(self, termino: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("📖 Diccionario Contextual ICFES")
        self.setFixedSize(400, 240)
        self.setWindowFlags(self.windowFlags() | Qt.Tool)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        info = GlosarioContextual.buscar(termino) or {}

        palabra_tit = info.get("palabra", termino.capitalize())
        lbl_pal = QLabel(f"🔍 {palabra_tit}")
        lbl_pal.setObjectName("subtitulo")
        layout.addWidget(lbl_pal)

        # Definición
        lbl_def = QLabel(f"<b>Significado:</b> {info.get('definicion', '')}")
        lbl_def.setWordWrap(True)
        lbl_def.setStyleSheet("font-size: 13px; color: #1E293B;")
        layout.addWidget(lbl_def)

        # Sinónimos
        lbl_sin = QLabel(f"<b>Sinónimos útiles:</b> <i>{info.get('sinonimos', '')}</i>")
        lbl_sin.setWordWrap(True)
        lbl_sin.setStyleSheet("font-size: 12px; color: #4338CA;")
        layout.addWidget(lbl_sin)

        # Ejemplo
        lbl_ej = QLabel(f"<b>Ejemplo:</b> «{info.get('ejemplo', '')}»")
        lbl_ej.setWordWrap(True)
        lbl_ej.setStyleSheet("font-size: 12px; color: #047857;")
        layout.addWidget(lbl_ej)

        layout.addStretch()

        btn_ok = QPushButton("Entendido")
        btn_ok.setObjectName("btn_secundario")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)


class DialogoRuletaBonificacion(QDialog):
    """Ruleta interactiva que premia el puntaje perfecto (100%)."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("🎰 ¡Ruleta de Bonificación por Maestría Total!")
        self.setFixedSize(460, 340)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        lbl_tit = QLabel("¡PUNTAJE PERFECTO (100%)!")
        lbl_tit.setObjectName("titulo_grande")
        lbl_tit.setStyleSheet("color: #D97706; font-size: 22px;")
        lbl_tit.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_tit)

        lbl_desc = QLabel("Por responder todas las preguntas a la perfección, Koko te otorga un giro de bonificación especial:")
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_desc)

        # Caja central del premio
        self.caja_premio = QFrame()
        self.caja_premio.setStyleSheet("background-color: #FEF3C7; border: 2px dashed #F59E0B; border-radius: 12px; padding: 20px;")
        l_caja = QVBoxLayout(self.caja_premio)

        self.lbl_icono_premio = QLabel("🎰")
        self.lbl_icono_premio.setStyleSheet("font-size: 48px;")
        self.lbl_icono_premio.setAlignment(Qt.AlignCenter)

        self.lbl_texto_premio = QLabel("¡Presiona para girar!")
        self.lbl_texto_premio.setStyleSheet("font-size: 18px; font-weight: bold; color: #92400E;")
        self.lbl_texto_premio.setAlignment(Qt.AlignCenter)

        l_caja.addWidget(self.lbl_icono_premio)
        l_caja.addWidget(self.lbl_texto_premio)
        layout.addWidget(self.caja_premio)

        self.btn_girar = QPushButton("🎲 ¡Girar la Ruleta de la Fortuna!")
        self.btn_girar.setObjectName("btn_exito")
        self.btn_girar.setFixedHeight(46)
        self.btn_girar.clicked.connect(self._girar)
        layout.addWidget(self.btn_girar)

        self.premio_obtenido: Optional[Dict[str, Any]] = None

    def _girar(self) -> None:
        from ..pedagogia.gamificacion import GestorGamificacion
        self.btn_girar.setEnabled(False)

        # Pequeña animación de ruleta con timer
        self._contador = 0
        self._timer = QTimer(self)
        self._timer.setInterval(80)
        self._timer.timeout.connect(self._animar_giro)
        self._timer.start()

    def _animar_giro(self) -> None:
        self._contador += 1
        iconos = ["🎁", "⭐", "⏱️", "💎", "🚀", "👑"]
        self.lbl_icono_premio.setText(random.choice(iconos))

        if self._contador > 15:
            self._timer.stop()
            from ..pedagogia.gamificacion import GestorGamificacion
            premio = GestorGamificacion.girar_ruleta_bonificacion()
            self.premio_obtenido = premio
            self.lbl_icono_premio.setText(premio["icono"])
            self.lbl_texto_premio.setText(premio["nombre"])
            self.btn_girar.setText("🎉 ¡Reclamar Bonificación!")
            self.btn_girar.setEnabled(True)
            self.btn_girar.clicked.disconnect()
            self.btn_girar.clicked.connect(self.accept)

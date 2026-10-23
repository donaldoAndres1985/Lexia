"""
Diálogo de Mini-Simulacro Oficial ICFES Saber 7.° (15 Preguntas, 25 Minutos).
Evalúa competencias globales y genera diagnóstico formal.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..lectura.simulacro import GestorSimulacro

logger = logging.getLogger(__name__)


class DialogoSimulacroICFES(QDialog):
    """Interfaz para presentar el Mini-Simulacro formal."""

    def __init__(self, gestor_simulacro: GestorSimulacro, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.gestor = gestor_simulacro
        self.setWindowTitle("📝 Mini-Simulacro Oficial Saber 7.° — Lectura Crítica")
        self.resize(850, 620)

        self._simulacro = self.gestor.generar_simulacro_15_preguntas()
        self._preguntas = self._simulacro["preguntas"]
        self._respuestas = [None] * len(self._preguntas)
        self._indice_actual = 0
        self._segundos_restantes = self._simulacro["duracion_segundos"]
        self._segundos_iniciales = self._segundos_restantes

        self._construir_ui()

        # Timer regresivo
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick_cronometro)
        self._timer.start()

        self._cargar_pregunta(0)

    def _construir_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 20)
        layout.setSpacing(12)

        # Barra superior con cronómetro
        cabecera = QHBoxLayout()
        tit = QLabel("Mini-Simulacro Saber 7.°")
        tit.setObjectName("titulo_grande")
        cabecera.addWidget(tit)
        cabecera.addStretch()

        self.lbl_cronometro = QLabel("⏱️ 25:00")
        self.lbl_cronometro.setStyleSheet("font-size: 18px; font-weight: bold; color: #DC2626; background: #FEE2E2; padding: 4px 12px; border-radius: 6px;")
        cabecera.addWidget(self.lbl_cronometro)
        layout.addLayout(cabecera)

        # Barra de progreso
        self.progreso = QProgressBar()
        self.progreso.setMaximum(len(self._preguntas))
        self.progreso.setFixedHeight(6)
        self.progreso.setTextVisible(False)
        layout.addWidget(self.progreso)

        # Contenedor de la pregunta
        self.tarjeta_preg = QFrame()
        self.tarjeta_preg.setObjectName("tarjeta")
        l_tarj = QVBoxLayout(self.tarjeta_preg)
        l_tarj.setSpacing(14)

        meta_layout = QHBoxLayout()
        self.lbl_texto_origen = QLabel("Texto")
        self.lbl_texto_origen.setStyleSheet("font-weight: bold; color: #4F46E5;")
        self.lbl_num = QLabel("Pregunta 1 de 15")
        self.lbl_num.setStyleSheet("color: #64748B; font-size: 12px;")
        meta_layout.addWidget(self.lbl_texto_origen)
        meta_layout.addStretch()
        meta_layout.addWidget(self.lbl_num)
        l_tarj.addLayout(meta_layout)

        self.lbl_enunciado = QLabel()
        self.lbl_enunciado.setWordWrap(True)
        self.lbl_enunciado.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E293B;")
        l_tarj.addWidget(self.lbl_enunciado)

        self.grupo_opciones = QButtonGroup(self)
        self.radios: List[QRadioButton] = []
        for i in range(4):
            r = QRadioButton(f"Opción {i + 1}")
            r.setStyleSheet("font-size: 14px; padding: 6px;")
            self.grupo_opciones.addButton(r, i)
            self.radios.append(r)
            l_tarj.addWidget(r)

        layout.addWidget(self.tarjeta_preg)
        layout.addStretch()

        # Botones de navegación
        pie = QHBoxLayout()
        self.btn_ant = QPushButton("← Anterior")
        self.btn_ant.setObjectName("btn_secundario")
        self.btn_ant.clicked.connect(self._anterior)
        pie.addWidget(self.btn_ant)

        pie.addStretch()

        self.btn_sig = QPushButton("Siguiente →")
        self.btn_sig.clicked.connect(self._siguiente)
        pie.addWidget(self.btn_sig)

        layout.addLayout(pie)

    def _tick_cronometro(self) -> None:
        self._segundos_restantes -= 1
        mins = self._segundos_restantes // 60
        segs = self._segundos_restantes % 60
        self.lbl_cronometro.setText(f"⏱️ {mins:02d}:{segs:02d}")

        if self._segundos_restantes <= 0:
            self._timer.stop()
            QMessageBox.warning(self, "Tiempo Agotado", "El tiempo límite de 25 minutos ha concluido. Calificando simulacro...")
            self._finalizar_simulacro()

    def _cargar_pregunta(self, idx: int) -> None:
        self._indice_actual = idx
        p = self._preguntas[idx]

        self.lbl_texto_origen.setText(f"📖 {p.get('titulo_lectura', 'Lectura')}")
        self.lbl_num.setText(f"Pregunta {idx + 1} de {len(self._preguntas)}  •  Nivel: {p.get('nivel', 'literal').capitalize()}")
        self.lbl_enunciado.setText(p.get("enunciado", ""))
        self.progreso.setValue(idx + 1)

        self.grupo_opciones.blockSignals(True)
        self.grupo_opciones.setExclusive(False)
        for r in self.radios:
            r.setChecked(False)
        self.grupo_opciones.setExclusive(True)

        for i, opt in enumerate(p.get("opciones", [])):
            if i < len(self.radios):
                self.radios[i].setText(opt)

        resp_ant = self._respuestas[idx]
        if resp_ant is not None and 0 <= resp_ant < 4:
            self.radios[resp_ant].setChecked(True)

        self.grupo_opciones.blockSignals(False)

        self.btn_ant.setEnabled(idx > 0)
        if idx == len(self._preguntas) - 1:
            self.btn_sig.setText("Finalizar Simulacro ✓")
            self.btn_sig.setObjectName("btn_exito")
        else:
            self.btn_sig.setText("Siguiente →")
            self.btn_sig.setObjectName("")

        self.btn_sig.style().unpolish(self.btn_sig)
        self.btn_sig.style().polish(self.btn_sig)

    def _guardar_seleccion(self) -> None:
        sel = self.grupo_opciones.checkedId()
        if sel != -1:
            self._respuestas[self._indice_actual] = sel

    def _anterior(self) -> None:
        self._guardar_seleccion()
        if self._indice_actual > 0:
            self._cargar_pregunta(self._indice_actual - 1)

    def _siguiente(self) -> None:
        self._guardar_seleccion()
        if self._indice_actual < len(self._preguntas) - 1:
            self._cargar_pregunta(self._indice_actual + 1)
        else:
            self._finalizar_simulacro()

    def _finalizar_simulacro(self) -> None:
        self._timer.stop()
        tiempo_empleado = self._segundos_iniciales - max(0, self._segundos_restantes)
        res = self.gestor.calificar_simulacro(self._preguntas, self._respuestas, tiempo_empleado)

        msg = (
            f"🎯 <b>Puntaje Global ICFES:</b> {res['puntaje_global']} / 100 puntos<br>"
            f"🏆 <b>Nivel de Desempeño:</b> <span style='color:#4F46E5;'>{res['nivel_desempeno']}</span><br>"
            f"📊 <b>Aciertos Totales:</b> {res['aciertos']} de {res['total_preguntas']}<br>"
            f"⏱️ <b>Tiempo Empleado:</b> {res['tiempo_minutos']} minutos<br><br>"
            f"<b>Diagnóstico de Competencias:</b><br>{res['diagnostico']}<br><br>"
            f"• Nivel Literal: {res['desglose_dimensiones']['literal']}<br>"
            f"• Nivel Inferencial: {res['desglose_dimensiones']['inferencial']}<br>"
            f"• Nivel Crítico: {res['desglose_dimensiones']['critico']}"
        )

        QMessageBox.information(self, "Resultado del Mini-Simulacro Saber 7.°", msg)
        self.accept()

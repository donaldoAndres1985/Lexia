"""
Panel de control del Modo Padre.
Configuración integral, visualización de estadísticas con Matplotlib y acciones directas.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ...config.configuracion import ConfiguracionSistema
from ...datos.repositorio import RepositorioDatos

logger = logging.getLogger(__name__)


class PanelPadre(QDialog):
    """Ventana principal de administración para padres."""

    liberacion_solicitada = Signal()
    minutos_ajustados = Signal(float)

    def __init__(self, configuracion: ConfiguracionSistema, repositorio: RepositorioDatos, parent=None):
        super().__init__(parent)
        self.config = configuracion
        self.repo = repositorio

        self.setWindowTitle("Lee y Juega — Panel de Control del Padre")
        self.resize(880, 640)
        self.setMinimumSize(800, 580)

        self._construir_ui()

    def _construir_ui(self) -> None:
        layout_principal = QVBoxLayout(self)

        # Encabezado
        encabezado = QHBoxLayout()
        titulo = QLabel("Panel de Administración y Control Parental")
        titulo.setObjectName("titulo_grande")
        encabezado.addWidget(titulo)
        encabezado.addStretch()

        btn_cerrar = QPushButton("Cerrar Panel")
        btn_cerrar.setObjectName("btn_secundario")
        btn_cerrar.clicked.connect(self.close)
        encabezado.addWidget(btn_cerrar)
        layout_principal.addLayout(encabezado)

        # Pestañas
        self.tabs = QTabWidget()
        self.tab_config = self._crear_tab_configuracion()
        self.tab_stats = self._crear_tab_estadisticas()
        self.tab_acciones = self._crear_tab_acciones()

        self.tabs.addTab(self.tab_config, "⚙️ Configuración")
        self.tabs.addTab(self.tab_stats, "📊 Estadísticas y Progreso")
        self.tabs.addTab(self.tab_acciones, "⚡ Acciones y Control")

        layout_principal.addWidget(self.tabs)

    # --- PESTAÑA 1: CONFIGURACIÓN ---

    def _crear_tab_configuracion(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()
        form.setSpacing(12)

        # 1. Tiempos
        self.spin_recompensa = QSpinBox()
        self.spin_recompensa.setRange(5, 300)
        self.spin_recompensa.setValue(int(self.config.obtener("tiempo_recompensa_min", 60)))
        self.spin_recompensa.setSuffix(" min")
        form.addRow("Recompensa por test aprobado:", self.spin_recompensa)

        self.spin_umbral = QSpinBox()
        self.spin_umbral.setRange(50, 100)
        self.spin_umbral.setValue(int(self.config.obtener("umbral_aprobacion", 70)))
        self.spin_umbral.setSuffix(" %")
        form.addRow("Umbral mínimo de aprobación:", self.spin_umbral)

        self.spin_ocio_inicial = QSpinBox()
        self.spin_ocio_inicial.setRange(0, 240)
        self.spin_ocio_inicial.setValue(int(self.config.obtener("tiempo_ocio_inicial_min", 0)))
        self.spin_ocio_inicial.setSuffix(" min")
        form.addRow("Tiempo de ocio inicial al comenzar el día:", self.spin_ocio_inicial)

        # 2. Listas de Ocio y Estudio
        self.txt_apps_ocio = QLineEdit(", ".join(self.config.obtener("apps_ocio", [])))
        form.addRow("Procesos bloqueados (Ocio):", self.txt_apps_ocio)

        self.txt_titulos_ocio = QLineEdit(", ".join(self.config.obtener("titulos_ocio", [])))
        form.addRow("Palabras clave de ocio en navegador:", self.txt_titulos_ocio)

        self.txt_titulos_estudio = QLineEdit(", ".join(self.config.obtener("titulos_estudio", [])))
        form.addRow("Palabras clave de estudio (no bloquea):", self.txt_titulos_estudio)

        # 3. Horarios
        h_layout = QHBoxLayout()
        self.time_inicio = QTimeEdit()
        self.time_inicio.setDisplayFormat("HH:mm")
        h_ini_str = self.config.obtener("horario_ocio_inicio", "08:00")
        self.time_inicio.setTime(self.time_inicio.time().fromString(h_ini_str, "HH:mm"))

        self.time_fin = QTimeEdit()
        self.time_fin.setDisplayFormat("HH:mm")
        h_fin_str = self.config.obtener("horario_ocio_fin", "21:00")
        self.time_fin.setTime(self.time_fin.time().fromString(h_fin_str, "HH:mm"))

        h_layout.addWidget(QLabel("Desde:"))
        h_layout.addWidget(self.time_inicio)
        h_layout.addWidget(QLabel("Hasta:"))
        h_layout.addWidget(self.time_fin)
        h_layout.addStretch()
        form.addRow("Horario de ocio permitido:", h_layout)

        # 4. API Key Gemini (cifrada con DPAPI)
        self.input_gemini = QLineEdit()
        self.input_gemini.setEchoMode(QLineEdit.Password)
        self.input_gemini.setText(self.config.obtener_gemini_api_key())
        self.input_gemini.setPlaceholderText("Clave de API de Gemini (dejar en blanco para usar banco offline)")
        form.addRow("Gemini API Key (Cifrada con DPAPI):", self.input_gemini)

        # 5. Opciones avanzadas
        self.chk_vigilante = QCheckBox("Activar proceso vigilante transparente (reinicia la app si se cierra)")
        self.chk_vigilante.setChecked(bool(self.config.obtener("vigilante_activo", True)))
        form.addRow("Seguridad:", self.chk_vigilante)

        layout.addLayout(form)
        layout.addStretch()

        btn_guardar = QPushButton("💾 Guardar Cambios de Configuración")
        btn_guardar.setObjectName("btn_exito")
        btn_guardar.clicked.connect(self._guardar_configuracion)
        layout.addWidget(btn_guardar)

        return widget

    def _guardar_configuracion(self) -> None:
        try:
            self.config.establecer("tiempo_recompensa_min", self.spin_recompensa.value(), False)
            self.config.establecer("umbral_aprobacion", self.spin_umbral.value(), False)
            self.config.establecer("tiempo_ocio_inicial_min", self.spin_ocio_inicial.value(), False)

            # Listas
            apps_o = [a.strip() for a in self.txt_apps_ocio.text().split(",") if a.strip()]
            tit_o = [t.strip() for t in self.txt_titulos_ocio.text().split(",") if t.strip()]
            tit_e = [t.strip() for t in self.txt_titulos_estudio.text().split(",") if t.strip()]
            self.config.establecer("apps_ocio", apps_o, False)
            self.config.establecer("titulos_ocio", tit_o, False)
            self.config.establecer("titulos_estudio", tit_e, False)

            # Horarios
            self.config.establecer("horario_ocio_inicio", self.time_inicio.time().toString("HH:mm"), False)
            self.config.establecer("horario_ocio_fin", self.time_fin.time().toString("HH:mm"), False)

            # Gemini
            self.config.establecer_gemini_api_key(self.input_gemini.text().strip())

            # Vigilante
            self.config.establecer("vigilante_activo", self.chk_vigilante.isChecked(), False)

            self.config.guardar()
            QMessageBox.information(self, "Configuración", "Configuración guardada correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la configuración: {e}")

    # --- PESTAÑA 2: ESTADÍSTICAS ---

    def _crear_tab_estadisticas(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        stats = self.repo.obtener_estadisticas_generales()

        # Cuadrícula de métricas rápidas
        grid = QGridLayout()
        grid.setSpacing(10)

        tarjetas = [
            ("Tests Aprobados", f"{stats['aprobados']} de {stats['total_tests']}", "#ECFDF5", "#047857"),
            ("Tasa de Aprobación", f"{stats['tasa_aprobacion']}%", "#EEF2FF", "#4338CA"),
            ("Nivel Actual", f"Nivel {stats['nivel_actual']}", "#FEF3C7", "#B45309"),
            ("Racha Actual", f"{stats['racha_dias']} días seguidos", "#FCE7F3", "#BE185D"),
            ("Comprensión Literal", f"{stats['pct_literal']}%", "#F1F5F9", "#1E293B"),
            ("Comprensión Inferencial", f"{stats['pct_inferencial']}%", "#F1F5F9", "#1E293B"),
            ("Pensamiento Crítico", f"{stats['pct_critico']}%", "#F1F5F9", "#1E293B"),
            ("Tiempo Jugado Total", f"{stats['minutos_jugados']} min", "#F1F5F9", "#1E293B"),
        ]

        for i, (tit, val, bg, fg) in enumerate(tarjetas):
            caja = QFrame()
            caja.setStyleSheet(f"background-color: {bg}; border-radius: 10px; padding: 10px;")
            l = QVBoxLayout(caja)
            l.setContentsMargins(6, 6, 6, 6)
            lbl_t = QLabel(tit)
            lbl_t.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {fg};")
            lbl_v = QLabel(val)
            lbl_v.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {fg};")
            l.addWidget(lbl_t)
            l.addWidget(lbl_v)
            grid.addWidget(caja, i // 4, i % 4)

        layout.addLayout(grid)

        # Gráfica embebida con Matplotlib
        figura = Figure(figsize=(7, 2.8), dpi=90)
        self.canvas = FigureCanvas(figura)
        layout.addWidget(self.canvas)

        self._dibujar_grafica_estadisticas(figura)

        # Botón para exportar reporte
        btn_exportar = QPushButton("📄 Exportar Reporte a CSV")
        btn_exportar.setObjectName("btn_secundario")
        btn_exportar.clicked.connect(self._exportar_csv)
        layout.addWidget(btn_exportar)

        return widget

    def _dibujar_grafica_estadisticas(self, figura: Figure) -> None:
        """Dibuja barras de actividad de lectura y juego de los últimos días."""
        ax = figura.add_subplot(111)
        datos_dias = self.repo.obtener_historial_tiempos_ultimos_dias(7)

        if not datos_dias:
            fechas = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Hoy"]
            ganados = [0, 0, 0, 0, 0, 0, 0]
            gastados = [0, 0, 0, 0, 0, 0, 0]
        else:
            fechas = [d["fecha"] for d in datos_dias]
            ganados = [d["ganados"] for d in datos_dias]
            gastados = [d["gastados"] for d in datos_dias]

        import numpy as np
        x = np.arange(len(fechas))
        ancho = 0.35

        ax.bar(x - ancho / 2, ganados, ancho, label="Minutos Ganados (Lectura)", color="#10B981")
        ax.bar(x + ancho / 2, gastados, ancho, label="Minutos Jugados (Ocio)", color="#F59E0B")

        ax.set_ylabel("Minutos")
        ax.set_title("Balance Semanal: Lectura vs. Ocio")
        ax.set_xticks(x)
        ax.set_xticklabels(fechas)
        ax.legend(loc="upper right", fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        figura.tight_layout()

    def _exportar_csv(self) -> None:
        ruta, _ = QFileDialog.getSaveFileName(self, "Exportar Historial", "Reporte_Lee_y_Juega.csv", "Archivos CSV (*.csv)")
        if ruta:
            if self.repo.exportar_csv(Path(ruta)):
                QMessageBox.information(self, "Exportación", f"Reporte exportado exitosamente a:\n{ruta}")
            else:
                QMessageBox.critical(self, "Error", "No se pudo exportar el archivo CSV.")

    # --- PESTAÑA 3: ACCIONES ---

    def _crear_tab_acciones(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        # 1. Liberar equipo
        grupo_liberar = QGroupBox("Liberación Inmediata")
        l_liberar = QVBoxLayout(grupo_liberar)
        lbl_info = QLabel("Si necesita usar el computador o permitir tiempo extraordinario:")
        btn_liberar = QPushButton("🔓 Liberar Equipo Ahora (Cerrar Pantalla de Bloqueo)")
        btn_liberar.setObjectName("btn_exito")
        btn_liberar.clicked.connect(self._al_liberar_equipo)
        l_liberar.addWidget(lbl_info)
        l_liberar.addWidget(btn_liberar)
        layout.addWidget(grupo_liberar)

        # 2. Ajuste manual de tiempo
        grupo_tiempo = QGroupBox("Ajuste Manual de Tiempo")
        l_tiempo = QHBoxLayout(grupo_tiempo)
        
        btn_mas_30 = QPushButton("🎁 Regalar +30 minutos")
        btn_mas_30.clicked.connect(lambda: self._ajustar_tiempo(30))

        btn_mas_60 = QPushButton("🎁 Regalar +60 minutos")
        btn_mas_60.clicked.connect(lambda: self._ajustar_tiempo(60))

        btn_menos_30 = QPushButton("⚠️ Retirar -30 minutos")
        btn_menos_30.setObjectName("btn_secundario")
        btn_menos_30.clicked.connect(lambda: self._ajustar_tiempo(-30))

        l_tiempo.addWidget(btn_mas_30)
        l_tiempo.addWidget(btn_mas_60)
        l_tiempo.addWidget(btn_menos_30)
        layout.addWidget(grupo_tiempo)

        # 3. Mantenimiento y Respaldos
        grupo_mant = QGroupBox("Mantenimiento y Respaldo")
        l_mant = QHBoxLayout(grupo_mant)

        btn_backup = QPushButton("💾 Respaldar Base de Datos")
        btn_backup.setObjectName("btn_secundario")
        btn_backup.clicked.connect(self._hacer_respaldo)

        btn_reset = QPushButton("🔄 Reiniciar Progreso")
        btn_reset.setStyleSheet("background-color: #EF4444; color: white;")
        btn_reset.clicked.connect(self._reiniciar_progreso)

        l_mant.addWidget(btn_backup)
        l_mant.addWidget(btn_reset)
        layout.addWidget(grupo_mant)

        layout.addStretch()
        return widget

    def _al_liberar_equipo(self) -> None:
        self.liberacion_solicitada.emit()
        QMessageBox.information(self, "Liberación", "El bloqueo ha sido levantado.")

    def _ajustar_tiempo(self, delta: float) -> None:
        self.minutos_ajustados.emit(delta)
        signo = "+" if delta > 0 else ""
        QMessageBox.information(self, "Tiempo", f"Se han ajustado {signo}{delta} minutos al balance de hoy.")

    def _hacer_respaldo(self) -> None:
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Respaldo", "respaldo_lee_y_juega.db", "SQLite DB (*.db)")
        if ruta:
            if self.repo.respaldar_base_datos(Path(ruta)):
                QMessageBox.information(self, "Respaldo", f"Copia de seguridad guardada en:\n{ruta}")
            else:
                QMessageBox.critical(self, "Error", "Fallo al generar el respaldo de la base de datos.")

    def _reiniciar_progreso(self) -> None:
        r = QMessageBox.question(
            self,
            "Confirmación",
            "¿Está seguro de que desea reiniciar el nivel pedagógico a 1?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if r == QMessageBox.Yes:
            self.repo.registrar_cambio_nivel(1, "Reinicio manual por el padre")
            QMessageBox.information(self, "Reinicio", "Nivel reiniciado a 1.")

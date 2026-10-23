"""
Ventana kiosco a pantalla completa para Lee y Juega.
Permanece siempre al frente cuando se agota el tiempo de ocio.
Contiene el flujo completo: bienvenida, lección interactiva previa, lectura,
test de opción múltiple, tutor y celebración de aprobación.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QPoint, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QCloseEvent, QColor, QFont, QKeyEvent, QPainter, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..datos.repositorio import RepositorioDatos
from ..lectura.calificacion import EvaluadorTest
from ..lectura.dificultad import GestorDificultadAdaptativa
from ..lectura.generador_preguntas import GeneradorPreguntas
from ..lectura.seleccion import SelectorLectura
from ..pedagogia.lecciones import GestorLecciones
from ..pedagogia.tutor import TutorPedagogico
from ..ui.padre.login import DialogoLoginPadre
from ..ui.padre.panel_padre import PanelPadre

logger = logging.getLogger(__name__)


class VentanaKiosco(QWidget):
    """
    Ventana kiosco a pantalla completa, sin bordes y siempre encima.
    Solo se desbloquea al aprobar la evaluación o mediante la clave del padre.
    """
    test_aprobado = Signal()
    desbloqueo_padre = Signal()

    def __init__(
        self,
        configuracion,
        repositorio: RepositorioDatos,
        selector_lectura: SelectorLectura,
        generador_preguntas: GeneradorPreguntas,
        gestor_lecciones: GestorLecciones,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.config = configuracion
        self.repo = repositorio
        self.selector = selector_lectura
        self.generador = generador_preguntas
        self.lecciones = gestor_lecciones
        self.dificultad = GestorDificultadAdaptativa(repositorio, configuracion)

        self._permitir_cierre = False
        self._lectura_actual: Optional[Dict[str, Any]] = None
        self._preguntas_actuales: List[Dict[str, Any]] = []
        self._tiempo_inicio_lectura = 0.0

        # Configuración de ventana Kiosco
        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose, False)

        # Timer para re-elevar y mantener foco si pierde el frente
        self._timer_reelevar = QTimer(self)
        self._timer_reelevar.setInterval(500)
        self._timer_reelevar.timeout.connect(self._asegurar_foco_frente)

        self._construir_interfaz()

    def _construir_interfaz(self) -> None:
        layout_raiz = QVBoxLayout(self)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        # Barra superior con estado y botón discreto de Modo Padre
        self.barra_superior = QFrame()
        self.barra_superior.setFixedHeight(50)
        self.barra_superior.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #E2E8F0;")
        layout_barra = QHBoxLayout(self.barra_superior)
        layout_barra.setContentsMargins(24, 0, 24, 0)

        self.lbl_logo = QLabel("📖 Lee y Juega")
        self.lbl_logo.setStyleSheet("font-weight: bold; font-size: 16px; color: #4F46E5;")
        layout_barra.addWidget(self.lbl_logo)

        self.lbl_estado_nivel = QLabel("Nivel 1 • Racha: 0 días")
        self.lbl_estado_nivel.setStyleSheet("color: #64748B; font-size: 13px;")
        layout_barra.addWidget(self.lbl_estado_nivel)

        layout_barra.addStretch()

        self.btn_modo_padre = QPushButton("🔐 Modo Padre")
        self.btn_modo_padre.setObjectName("btn_padre")
        self.btn_modo_padre.clicked.connect(self._abrir_modo_padre)
        layout_barra.addWidget(self.btn_modo_padre)

        layout_raiz.addWidget(self.barra_superior)

        # Contenedor apilado para las distintas vistas del flujo
        self.stack = QStackedWidget()
        
        self.vista_bienvenida = self._crear_vista_bienvenida()
        self.vista_leccion = self._crear_vista_leccion()
        self.vista_lectura = self._crear_vista_lectura()
        self.vista_test = self._crear_vista_test()
        self.vista_resultado = self._crear_vista_resultado()

        self.stack.addWidget(self.vista_bienvenida)  # Index 0
        self.stack.addWidget(self.vista_leccion)     # Index 1
        self.stack.addWidget(self.vista_lectura)     # Index 2
        self.stack.addWidget(self.vista_test)        # Index 3
        self.stack.addWidget(self.vista_resultado)   # Index 4

        layout_raiz.addWidget(self.stack)

    # --- VISTA 0: BIENVENIDA ---

    def _crear_vista_bienvenida(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setFixedWidth(680)
        l_tarjeta = QVBoxLayout(tarjeta)
        l_tarjeta.setSpacing(20)
        l_tarjeta.setContentsMargins(36, 36, 36, 36)

        self.lbl_saludo = QLabel("¡Hola, campeona!")
        self.lbl_saludo.setObjectName("titulo_grande")
        self.lbl_saludo.setAlignment(Qt.AlignCenter)
        l_tarjeta.addWidget(self.lbl_saludo)

        self.lbl_motivo = QLabel(
            "Tu tiempo de juego ha concluido por ahora.<br>"
            "Para desbloquear tu computador y ganar <b>60 minutos</b> más de ocio, "
            "vamos a leer un texto interesante de tu nivel y resolver un breve test."
        )
        self.lbl_motivo.setAlignment(Qt.AlignCenter)
        self.lbl_motivo.setWordWrap(True)
        self.lbl_motivo.setStyleSheet("font-size: 16px; line-height: 1.5; color: #334155;")
        l_tarjeta.addWidget(self.lbl_motivo)

        # Tarjeta pequeña de métricas
        tarjeta_resumen = QFrame()
        tarjeta_resumen.setObjectName("tarjeta_destacada")
        l_res = QHBoxLayout(tarjeta_resumen)
        
        self.lbl_badge_nivel = QLabel("🎯 Nivel 1")
        self.lbl_badge_nivel.setStyleSheet("font-weight: bold; color: #4F46E5;")
        self.lbl_badge_recompensa = QLabel("🎁 Recompensa: +60 min")
        self.lbl_badge_recompensa.setStyleSheet("font-weight: bold; color: #10B981;")
        self.lbl_badge_racha = QLabel("🔥 Racha: 0 días")
        self.lbl_badge_racha.setStyleSheet("font-weight: bold; color: #F59E0B;")

        l_res.addWidget(self.lbl_badge_nivel)
        l_res.addWidget(self.lbl_badge_recompensa)
        l_res.addWidget(self.lbl_badge_racha)
        l_tarjeta.addWidget(tarjeta_resumen)

        btn_comenzar = QPushButton("🚀 ¡Vamos a leer para jugar!")
        btn_comenzar.setFixedHeight(48)
        btn_comenzar.setStyleSheet("font-size: 16px;")
        btn_comenzar.clicked.connect(self._iniciar_flujo_lectura)
        l_tarjeta.addWidget(btn_comenzar)

        layout.addWidget(tarjeta)
        return widget

    # --- VISTA 1: LECCIÓN INTERACTIVA (ENSEÑAR PRIMERO) ---

    def _crear_vista_leccion(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setFixedSize(780, 520)
        l_tarjeta = QVBoxLayout(tarjeta)
        l_tarjeta.setSpacing(16)
        l_tarjeta.setContentsMargins(28, 28, 28, 28)

        self.lbl_leccion_titulo = QLabel("Lección")
        self.lbl_leccion_titulo.setObjectName("subtitulo")
        l_tarjeta.addWidget(self.lbl_leccion_titulo)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        contenido_scroll = QWidget()
        self.l_leccion_scroll = QVBoxLayout(contenido_scroll)
        self.l_leccion_scroll.setSpacing(14)

        self.lbl_leccion_intro = QLabel()
        self.lbl_leccion_intro.setWordWrap(True)
        self.l_leccion_scroll.addWidget(self.lbl_leccion_intro)

        self.caja_ejemplo = QFrame()
        self.caja_ejemplo.setObjectName("tarjeta_destacada")
        l_ej = QVBoxLayout(self.caja_ejemplo)
        self.lbl_leccion_ejemplo = QLabel()
        self.lbl_leccion_ejemplo.setWordWrap(True)
        l_ej.addWidget(self.lbl_leccion_ejemplo)
        self.l_leccion_scroll.addWidget(self.caja_ejemplo)

        self.lbl_leccion_consejos = QLabel()
        self.lbl_leccion_consejos.setWordWrap(True)
        self.l_leccion_scroll.addWidget(self.lbl_leccion_consejos)

        scroll.setWidget(contenido_scroll)
        l_tarjeta.addWidget(scroll)

        btn_continuar = QPushButton("¡Entendido! Pasar a la lectura →")
        btn_continuar.setFixedHeight(44)
        btn_continuar.clicked.connect(self._continuar_a_lectura)
        l_tarjeta.addWidget(btn_continuar)

        layout.addWidget(tarjeta)
        return widget

    # --- VISTA 2: LECTURA DEL TEXTO ---

    def _crear_vista_lectura(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 20, 40, 24)
        layout.setSpacing(14)

        # Cabecera de la lectura
        cabecera = QHBoxLayout()
        self.lbl_lectura_titulo = QLabel("Título de la lectura")
        self.lbl_lectura_titulo.setObjectName("titulo_grande")
        cabecera.addWidget(self.lbl_lectura_titulo)
        cabecera.addStretch()

        self.lbl_cronometro = QLabel("⏱️ Tiempo: 00:00")
        self.lbl_cronometro.setStyleSheet("font-size: 14px; font-weight: bold; color: #4F46E5;")
        cabecera.addWidget(self.lbl_cronometro)
        layout.addLayout(cabecera)

        self.lbl_fuente = QLabel("Fuente")
        self.lbl_fuente.setStyleSheet("color: #64748B; font-size: 12px;")
        layout.addWidget(self.lbl_fuente)

        # Área de scroll para el texto
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.contenedor_texto = QWidget()
        self.l_texto = QVBoxLayout(self.contenedor_texto)
        self.l_texto.setContentsMargins(10, 10, 10, 10)

        # Imagen para textos discontinuos
        self.lbl_imagen_discontinua = QLabel()
        self.lbl_imagen_discontinua.setAlignment(Qt.AlignCenter)
        self.lbl_imagen_discontinua.setVisible(False)
        self.l_texto.addWidget(self.lbl_imagen_discontinua)

        self.lbl_cuerpo_texto = QLabel()
        self.lbl_cuerpo_texto.setWordWrap(True)
        self.lbl_cuerpo_texto.setStyleSheet("font-size: 17px; line-height: 1.6; color: #1E293B;")
        self.l_texto.addWidget(self.lbl_cuerpo_texto)

        scroll.setWidget(self.contenedor_texto)
        layout.addWidget(scroll)

        # Botón para comenzar el test
        pie = QHBoxLayout()
        pie.addStretch()
        self.btn_iniciar_test = QPushButton("✍️ ¡Terminé de leer, comenzar el Test! →")
        self.btn_iniciar_test.setFixedHeight(48)
        self.btn_iniciar_test.setFixedWidth(340)
        self.btn_iniciar_test.clicked.connect(self._mostrar_test)
        pie.addWidget(self.btn_iniciar_test)
        pie.addStretch()
        layout.addLayout(pie)

        # Temporizador de lectura suave
        self._timer_lectura = QTimer(self)
        self._timer_lectura.setInterval(1000)
        self._timer_lectura.timeout.connect(self._actualizar_cronometro)

        return widget

    # --- VISTA 3: TEST DE OPCIÓN MÚLTIPLE ---

    def _crear_vista_test(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 20, 40, 24)
        layout.setSpacing(14)

        # Barra de progreso del test
        cabecera = QHBoxLayout()
        self.lbl_num_pregunta = QLabel("Pregunta 1 de 5")
        self.lbl_num_pregunta.setObjectName("subtitulo")
        cabecera.addWidget(self.lbl_num_pregunta)

        cabecera.addStretch()

        self.btn_volver_a_leer = QPushButton("📖 Releer el texto")
        self.btn_volver_a_leer.setObjectName("btn_secundario")
        self.btn_volver_a_leer.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        cabecera.addWidget(self.btn_volver_a_leer)

        layout.addLayout(cabecera)

        self.progreso_test = QProgressBar()
        self.progreso_test.setFixedHeight(8)
        self.progreso_test.setTextVisible(False)
        self.progreso_test.setStyleSheet("QProgressBar::chunk { background-color: #4F46E5; border-radius: 4px; }")
        layout.addWidget(self.progreso_test)

        # Tarjeta de la pregunta actual
        tarjeta_preg = QFrame()
        tarjeta_preg.setObjectName("tarjeta")
        l_preg = QVBoxLayout(tarjeta_preg)
        l_preg.setSpacing(16)
        l_preg.setContentsMargins(24, 24, 24, 24)

        self.lbl_dimension_badge = QLabel("Nivel: Literal")
        self.lbl_dimension_badge.setStyleSheet("font-size: 11px; font-weight: bold; color: #4F46E5; background-color: #EEF2FF; padding: 4px 8px; border-radius: 6px;")
        l_preg.addWidget(self.lbl_dimension_badge, alignment=Qt.AlignLeft)

        self.lbl_enunciado = QLabel("Enunciado de la pregunta")
        self.lbl_enunciado.setWordWrap(True)
        self.lbl_enunciado.setStyleSheet("font-size: 17px; font-weight: bold; color: #1E293B;")
        l_preg.addWidget(self.lbl_enunciado)

        # Opciones A, B, C, D
        self.grupo_opciones = QButtonGroup(self)
        self.radios_opciones: List[QRadioButton] = []

        for i in range(4):
            radio = QRadioButton(f"Opción {i + 1}")
            radio.setStyleSheet("font-size: 15px; padding: 6px;")
            self.grupo_opciones.addButton(radio, i)
            self.radios_opciones.append(radio)
            l_preg.addWidget(radio)

        layout.addWidget(tarjeta_preg)
        layout.addStretch()

        # Botones de navegación
        pie = QHBoxLayout()
        self.btn_anterior_preg = QPushButton("← Anterior")
        self.btn_anterior_preg.setObjectName("btn_secundario")
        self.btn_anterior_preg.clicked.connect(self._anterior_pregunta)
        pie.addWidget(self.btn_anterior_preg)

        pie.addStretch()

        self.btn_siguiente_preg = QPushButton("Siguiente →")
        self.btn_siguiente_preg.clicked.connect(self._siguiente_pregunta)
        pie.addWidget(self.btn_siguiente_preg)

        layout.addLayout(pie)
        return widget

    # --- VISTA 4: RESULTADO Y TUTOR ---

    def _crear_vista_resultado(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setFixedSize(760, 540)
        l_tarjeta = QVBoxLayout(tarjeta)
        l_tarjeta.setSpacing(16)
        l_tarjeta.setContentsMargins(28, 28, 28, 28)

        self.lbl_resultado_icono = QLabel("🎉")
        self.lbl_resultado_icono.setStyleSheet("font-size: 40px;")
        self.lbl_resultado_icono.setAlignment(Qt.AlignCenter)
        l_tarjeta.addWidget(self.lbl_resultado_icono)

        self.lbl_resultado_titulo = QLabel("¡Test Aprobado!")
        self.lbl_resultado_titulo.setObjectName("titulo_grande")
        self.lbl_resultado_titulo.setAlignment(Qt.AlignCenter)
        l_tarjeta.addWidget(self.lbl_resultado_titulo)

        self.lbl_resultado_puntaje = QLabel("Puntaje: 80% (4 de 5 aciertos)")
        self.lbl_resultado_puntaje.setAlignment(Qt.AlignCenter)
        self.lbl_resultado_puntaje.setStyleSheet("font-size: 16px; font-weight: bold; color: #10B981;")
        l_tarjeta.addWidget(self.lbl_resultado_puntaje)

        # Explicación del tutor en scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        contenido_scroll = QWidget()
        self.l_tutor_retro = QVBoxLayout(contenido_scroll)
        self.lbl_tutor_texto = QLabel()
        self.lbl_tutor_texto.setWordWrap(True)
        self.l_tutor_retro.addWidget(self.lbl_tutor_texto)

        scroll.setWidget(contenido_scroll)
        l_tarjeta.addWidget(scroll)

        # Botón de acción final
        self.btn_accion_final = QPushButton("🎮 ¡Disfrutar de mis 60 minutos ganados!")
        self.btn_accion_final.setObjectName("btn_exito")
        self.btn_accion_final.setFixedHeight(48)
        self.btn_accion_final.clicked.connect(self._finalizar_sesion)
        l_tarjeta.addWidget(self.btn_accion_final)

        layout.addWidget(tarjeta)
        return widget

    # --- CONTROL DE NAVEGACIÓN Y FLUJO ---

    def activar(self, motivo: str = "") -> None:
        """Muestra el kiosco en pantalla completa y bloquea."""
        self._permitir_cierre = False
        nivel = self.repo.obtener_nivel_actual()
        racha = self.repo.calcular_racha_dias()

        self.lbl_saludo.setText("¡A leer para jugar!")
        self.lbl_badge_nivel.setText(f"🎯 Nivel {nivel}")
        min_recompensa = self.config.obtener("tiempo_recompensa_min", 60)
        self.lbl_badge_recompensa.setText(f"🎁 Recompensa: +{min_recompensa} min")
        self.lbl_badge_racha.setText(f"🔥 Racha: {racha} días")
        self.lbl_estado_nivel.setText(f"Nivel {nivel} • Racha: {racha} días")

        if motivo:
            self.lbl_motivo.setText(f"{motivo}<br><br>Lee el texto con atención y aprueba el test para ganar <b>{min_recompensa} minutos</b> de juego.")

        self.stack.setCurrentIndex(0)
        self.showFullScreen()
        self._timer_reelevar.start()
        self._asegurar_foco_frente()
        logger.info("Ventana kiosco mostrada a pantalla completa.")

    def _asegurar_foco_frente(self) -> None:
        """Re-eleva periódicamente la ventana sin interceptar teclas del sistema."""
        if not self._permitir_cierre and self.isVisible():
            self.raise_()
            self.activateWindow()

    def _iniciar_flujo_lectura(self) -> None:
        """Selecciona lectura y evalúa si corresponde mostrar lección interactiva previa."""
        nivel = self.repo.obtener_nivel_actual()
        self._lectura_actual = self.selector.seleccionar_lectura(nivel)

        # Generar o cargar preguntas
        respaldo = self._lectura_actual.get("preguntas", [])
        self._preguntas_actuales = self.generador.generar_preguntas(
            self._lectura_actual.get("texto", ""),
            self._lectura_actual.get("titulo", ""),
            nivel,
            respaldo_preguntas=respaldo,
        )

        # Determinar si requiere lección interactiva (sección 6: Enseñar primero)
        primera_dimension = self._preguntas_actuales[0].get("nivel", "literal") if self._preguntas_actuales else "literal"
        if self.lecciones.debe_mostrar_leccion(primera_dimension):
            self._mostrar_leccion(primera_dimension)
        else:
            self._continuar_a_lectura()

    def _mostrar_leccion(self, tipo_leccion: str) -> None:
        """Carga la lección formativa interactiva en la vista 1."""
        contenido = self.lecciones.obtener_contenido_leccion(tipo_leccion)
        self.lbl_leccion_titulo.setText(contenido["titulo"])
        self.lbl_leccion_intro.setText(contenido["introduccion"])
        self.lbl_leccion_ejemplo.setText(f"<b>Ejemplo:</b> {contenido['ejemplo']['texto_ejemplo']}<br><br>{contenido['ejemplo']['explicacion_paso_a_paso']}")
        
        consejos_html = "<b>Consejos prácticos:</b><br>" + "<br>".join([f"• {c}" for c in contenido["consejos"]])
        self.lbl_leccion_consejos.setText(consejos_html)

        self._leccion_actual_tipo = tipo_leccion
        self.stack.setCurrentIndex(1)

    def _continuar_a_lectura(self) -> None:
        """Presenta la lectura en la vista 2."""
        if hasattr(self, "_leccion_actual_tipo"):
            self.lecciones.marcar_completada(self._leccion_actual_tipo)

        self.lbl_lectura_titulo.setText(self._lectura_actual.get("titulo", "Lectura"))
        self.lbl_fuente.setText(f"Fuente: {self._lectura_actual.get('fuente', 'Banco Lee y Juega')} | Nivel {self._lectura_actual.get('nivel', 1)}")

        # Manejo de imágenes para textos discontinuos
        ruta_img = self._lectura_actual.get("ruta_imagen")
        if ruta_img and Path(ruta_img).exists():
            pixmap = QPixmap(ruta_img)
            self.lbl_imagen_discontinua.setPixmap(pixmap.scaledToWidth(680, Qt.SmoothTransformation))
            self.lbl_imagen_discontinua.setVisible(True)
        else:
            self.lbl_imagen_discontinua.setVisible(False)

        texto_mostrar = self._lectura_actual.get("texto", "") or self._lectura_actual.get("texto_contexto", "")
        self.lbl_cuerpo_texto.setText(texto_mostrar)

        # Reiniciar cronómetro
        self._tiempo_inicio_lectura = time.time()
        self._timer_lectura.start()

        self.stack.setCurrentIndex(2)

    def _actualizar_cronometro(self) -> None:
        segundos = int(time.time() - self._tiempo_inicio_lectura)
        mins = segundos // 60
        segs = segundos % 60
        self.lbl_cronometro.setText(f"⏱️ Tiempo: {mins:02d}:{segs:02d}")

    def _mostrar_test(self) -> None:
        """Pasa de la lectura a la vista 3 del test interactivo."""
        self._timer_lectura.stop()
        self._respuestas_usuario = [None] * len(self._preguntas_actuales)
        self._indice_pregunta = 0
        self.progreso_test.setMaximum(len(self._preguntas_actuales))
        self._cargar_pregunta_test(0)
        self.stack.setCurrentIndex(3)

    def _cargar_pregunta_test(self, indice: int) -> None:
        if 0 <= indice < len(self._preguntas_actuales):
            self._indice_pregunta = indice
            preg = self._preguntas_actuales[indice]

            self.lbl_num_pregunta.setText(f"Pregunta {indice + 1} de {len(self._preguntas_actuales)}")
            self.progreso_test.setValue(indice + 1)

            dim = preg.get("nivel", "literal").capitalize()
            self.lbl_dimension_badge.setText(f"Dimensión ICFES: {dim}")
            self.lbl_enunciado.setText(preg.get("enunciado", ""))

            # Desconectar temporalmente para cargar opciones
            self.grupo_opciones.blockSignals(True)
            self.grupo_opciones.setExclusive(False)
            for r in self.radios_opciones:
                r.setChecked(False)
            self.grupo_opciones.setExclusive(True)

            opciones = preg.get("opciones", [])
            for i, opt in enumerate(opciones):
                if i < len(self.radios_opciones):
                    self.radios_opciones[i].setText(opt)

            # Restaurar respuesta previa si existe
            resp_previa = self._respuestas_usuario[indice]
            if resp_previa is not None and 0 <= resp_previa < 4:
                self.radios_opciones[resp_previa].setChecked(True)

            self.grupo_opciones.blockSignals(False)

            self.btn_anterior_preg.setEnabled(indice > 0)
            if indice == len(self._preguntas_actuales) - 1:
                self.btn_siguiente_preg.setText("Finalizar y Calificar ✓")
                self.btn_siguiente_preg.setObjectName("btn_exito")
            else:
                self.btn_siguiente_preg.setText("Siguiente →")
                self.btn_siguiente_preg.setObjectName("")
            
            # Recargar hoja de estilos para aplicar colores de botón
            self.btn_siguiente_preg.style().unpolish(self.btn_siguiente_preg)
            self.btn_siguiente_preg.style().polish(self.btn_siguiente_preg)

    def _guardar_seleccion_actual(self) -> None:
        sel = self.grupo_opciones.checkedId()
        if sel != -1:
            self._respuestas_usuario[self._indice_pregunta] = sel

    def _anterior_pregunta(self) -> None:
        self._guardar_seleccion_actual()
        if self._indice_pregunta > 0:
            self._cargar_pregunta_test(self._indice_pregunta - 1)

    def _siguiente_pregunta(self) -> None:
        self._guardar_seleccion_actual()
        
        # Validar que haya respondido
        if self._respuestas_usuario[self._indice_pregunta] is None:
            QMessageBox.information(self, "Atención", "Por favor, elige una de las opciones antes de continuar.")
            return

        if self._indice_pregunta < len(self._preguntas_actuales) - 1:
            self._cargar_pregunta_test(self._indice_pregunta + 1)
        else:
            self._calificar_test()

    def _calificar_test(self) -> None:
        """Evalúa las respuestas, registra en base de datos y muestra feedback del tutor."""
        umbral = float(self.config.obtener("umbral_aprobacion", 70.0))
        evaluador = EvaluadorTest(umbral)
        resultado = evaluador.evaluar(self._preguntas_actuales, self._respuestas_usuario)

        duracion_segundos = int(time.time() - self._tiempo_inicio_lectura)
        palabras = len(self._lectura_actual.get("texto", "").split())
        
        # Guardar en base de datos
        sesion_id = self.repo.guardar_sesion_lectura(
            titulo=self._lectura_actual.get("titulo", "Lectura"),
            tipo_texto=self._lectura_actual.get("tipo_texto", "literario"),
            subtipo=self._lectura_actual.get("subtipo"),
            nivel=self._lectura_actual.get("nivel", 1),
            fuente=self._lectura_actual.get("fuente", "banco_offline"),
            palabras=palabras,
            duracion_segundos=duracion_segundos,
        )

        desglose = resultado["desglose"]
        self.repo.guardar_test_resultado(
            sesion_id=sesion_id,
            nivel=self._lectura_actual.get("nivel", 1),
            total_preguntas=resultado["total_preguntas"],
            aciertos=resultado["aciertos"],
            puntaje_porcentaje=resultado["puntaje_porcentaje"],
            aprobado=resultado["aprobado"],
            aciertos_literal=desglose["literal"]["aciertos"],
            total_literal=desglose["literal"]["total"],
            aciertos_inferencial=desglose["inferencial"]["aciertos"],
            total_inferencial=desglose["inferencial"]["total"],
            aciertos_critico=desglose["critico"]["aciertos"],
            total_critico=desglose["critico"]["total"],
            detalle=resultado,
        )

        # Actualizar dificultad adaptativa
        nuevo_nivel, mensaje_nivel = self.dificultad.verificar_y_actualizar_nivel()

        # Presentar resultado
        aprobado = resultado["aprobado"]
        if aprobado:
            self.lbl_resultado_icono.setText("🌟 ¡LO LOGRASTE! 🌟")
            self.lbl_resultado_titulo.setText("¡Felicitaciones! Has aprobado el test.")
            self.lbl_resultado_puntaje.setStyleSheet("font-size: 18px; font-weight: bold; color: #10B981;")
            self.btn_accion_final.setText("🎮 ¡Disfrutar de mis minutos ganados y desbloquear!")
            self.btn_accion_final.setObjectName("btn_exito")
        else:
            self.lbl_resultado_icono.setText("🌱 ¡Buen esfuerzo! 🌱")
            self.lbl_resultado_titulo.setText("Estuviste cerca. Vamos a repasar las pistas.")
            self.lbl_resultado_puntaje.setStyleSheet("font-size: 18px; font-weight: bold; color: #F59E0B;")
            self.btn_accion_final.setText("🔄 Intentar con otra lectura")
            self.btn_accion_final.setObjectName("btn_secundario")

        self.btn_accion_final.style().unpolish(self.btn_accion_final)
        self.btn_accion_final.style().polish(self.btn_accion_final)

        self.lbl_resultado_puntaje.setText(
            f"Puntaje: {resultado['puntaje_porcentaje']}% ({resultado['aciertos']} de {resultado['total_preguntas']} aciertos)"
        )

        # Construir explicación pedagógica del tutor
        resumen_tutor = TutorPedagogico.generar_resumen_tutor(desglose, aprobado)
        if mensaje_nivel:
            resumen_tutor += f"<br><br><b>Nivel adaptativo:</b> {mensaje_nivel}"

        # Si no aprobó, detallar cada pregunta fallida con la explicación del tutor
        if not aprobado:
            resumen_tutor += "<br><br><b>Revisión de respuestas:</b><br>"
            for det in resultado["detalle_preguntas"]:
                if not det["es_correcta"]:
                    corr_txt = det["opciones"][det["correcta"]]
                    ele_txt = det["opciones"][det["seleccionada"]] if det["seleccionada"] is not None else "Sin responder"
                    resumen_tutor += TutorPedagogico.obtener_explicacion_error(
                        det["enunciado"], corr_txt, ele_txt, det["explicacion"], det["nivel"]
                    ) + "<br>"

        self.lbl_tutor_texto.setText(resumen_tutor)
        self._ultimo_aprobado = aprobado
        self.stack.setCurrentIndex(4)

    def _finalizar_sesion(self) -> None:
        """Si aprobó, emite la señal de test aprobado; si no, ofrece otra lectura."""
        if getattr(self, "_ultimo_aprobado", False):
            self._permitir_cierre = True
            self._timer_reelevar.stop()
            self.hide()
            self.test_aprobado.emit()
        else:
            # Reintentar con una lectura fresca
            self._iniciar_flujo_lectura()

    def _abrir_modo_padre(self) -> None:
        """Acceso al modo padre mediante clave Argon2."""
        dialogo = DialogoLoginPadre(self.config, self)
        if dialogo.exec() == QDialog.Accepted:
            panel = PanelPadre(self.config, self.repo, self)
            panel.liberacion_solicitada.connect(self._liberar_por_padre)
            panel.exec()

    def _liberar_por_padre(self) -> None:
        self._permitir_cierre = True
        self._timer_reelevar.stop()
        self.hide()
        self.desbloqueo_padre.emit()

    # --- PROTECCIÓN DE CIERRE KIOSCO ---

    def closeEvent(self, event: QCloseEvent) -> None:
        """Impide el cierre con Alt+F4 a menos que esté autorizado."""
        if self._permitir_cierre:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Ignora teclas de escape o combinaciones locales de cierre."""
        if event.key() == Qt.Key_Escape:
            event.ignore()
            return
        super().keyPressEvent(event)

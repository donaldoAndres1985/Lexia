"""
Punto de entrada principal de Lee y Juega.
Inicializa el sistema, monitoreo en segundo plano, bandeja del sistema
y el controlador de bloqueo kiosco.
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from .bloqueo.ventana_kiosco import VentanaKiosco
from .config.configuracion import ConfiguracionSistema, obtener_ruta_datos
from .datos.repositorio import RepositorioDatos
from .lectura.fuentes import GestorFuentesLectura
from .lectura.generador_preguntas import GeneradorPreguntas
from .lectura.seleccion import SelectorLectura
from .nucleo.banco_tiempo import BancoTiempo
from .nucleo.controlador_bloqueo import ControladorBloqueo
from .nucleo.monitor_actividad import MonitorActividad
from .nucleo.vigilante import VigilanteProceso
from .pedagogia.lecciones import GestorLecciones
from .ui.bandeja import BandejaSistema
from .ui.estilos.tema import obtener_estilo_general
from .ui.padre.login import DialogoLoginPadre
from .ui.padre.panel_padre import PanelPadre

# Configurar logging en archivo y consola
ruta_logs = obtener_ruta_datos() / "logs"
ruta_logs.mkdir(parents=True, exist_ok=True)
archivo_log = ruta_logs / "lee_y_juega.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler(archivo_log, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("LeeYJuega")


def registrar_inicio_con_windows(activar: bool = True) -> None:
    """Configura el inicio automático con la sesión de Windows en el registro."""
    if sys.platform != "win32":
        return

    try:
        import winreg
        clave_run = r"Software\Microsoft\Windows\CurrentVersion\Run"
        nombre_app = "LeeYJuega"

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, clave_run, 0, winreg.KEY_SET_VALUE) as key:
            if activar:
                # Si está congelado por PyInstaller o ejecutándose como script
                if getattr(sys, "frozen", False):
                    ruta_ejecutable = f'"{sys.executable}"'
                else:
                    ruta_script = Path(__file__).resolve().parent.parent.parent / "run.py"
                    ruta_ejecutable = f'"{sys.executable}" "{ruta_script}"'
                
                winreg.SetValueEx(key, nombre_app, 0, winreg.REG_SZ, ruta_ejecutable)
                logger.info("Registro de inicio con Windows configurado exitosamente.")
            else:
                try:
                    winreg.DeleteValue(key, nombre_app)
                    logger.info("Registro de inicio con Windows eliminado.")
                except FileNotFoundError:
                    pass
    except Exception as e:
        logger.warning(f"No se pudo registrar el inicio automático en Windows: {e}")


def main() -> int:
    """Función principal de ejecución."""
    logger.info("Iniciando Lee y Juega v1.0.0...")

    # Permitir que el proceso vigilante esté activo
    VigilanteProceso.reanudar()

    app = QApplication(sys.argv)
    app.setApplicationName("Lee y Juega")
    app.setQuitOnLastWindowClosed(False)  # Mantener vivo en la bandeja
    app.setStyleSheet(obtener_estilo_general())

    # 1. Configuración y Base de Datos
    config = ConfiguracionSistema()
    repo = RepositorioDatos()

    if config.obtener("arrancar_con_windows", True):
        registrar_inicio_con_windows(True)

    # 2. Servicios pedagógicos y de lectura
    fuentes = GestorFuentesLectura()
    selector = SelectorLectura(fuentes)
    generador = GeneradorPreguntas(config)
    lecciones = GestorLecciones(repo)

    # 3. Núcleo: Monitor, Banco y Controlador
    monitor = MonitorActividad(config, intervalo_segundos=3.0)
    banco = BancoTiempo(repo, config)
    controlador = ControladorBloqueo(monitor, banco)

    # 4. Interfaz de Bloqueo Kiosco
    kiosco = VentanaKiosco(
        configuracion=config,
        repositorio=repo,
        selector_lectura=selector,
        generador_preguntas=generador,
        gestor_lecciones=lecciones,
    )

    # Conectar señales del bloqueo
    controlador.solicitar_bloqueo.connect(kiosco.activar)
    controlador.solicitar_desbloqueo.connect(kiosco.hide)

    kiosco.test_aprobado.connect(lambda: banco.agregar_recompensa_lectura())
    kiosco.test_aprobado.connect(lambda: controlador.desactivar_bloqueo())
    kiosco.desbloqueo_padre.connect(lambda: controlador.desactivar_bloqueo())

    # 5. Bandeja del sistema
    bandeja = BandejaSistema(banco)
    bandeja.iniciar()

    def abrir_panel_padre():
        dialogo = DialogoLoginPadre(config)
        if dialogo.exec() == QDialog.Accepted:
            panel = PanelPadre(config, repo)
            panel.liberacion_solicitada.connect(lambda: controlador.desactivar_bloqueo())
            panel.minutos_ajustados.connect(lambda d: banco.ajustar_manualmente(d))
            panel.exec()

    def salir_seguro():
        dialogo = DialogoLoginPadre(config)
        if dialogo.exec() == QDialog.Accepted:
            logger.info("Cierre autorizado por el padre.")
            VigilanteProceso.solicitar_parada()
            bandeja.ocultar()
            app.quit()

    def mostrar_lecciones_menu():
        kiosco.activar("📚 Modo Aprendizaje: explora una lección guiada.")

    bandeja.solicitar_modo_padre.connect(abrir_panel_padre)
    bandeja.solicitar_salir.connect(salir_seguro)
    bandeja.solicitar_lecciones.connect(mostrar_lecciones_menu)

    # Iniciar monitor
    monitor.iniciar()

    # Si al arrancar el saldo es 0 y se abre en ocio, el monitor activará el bloqueo
    logger.info(f"Sistema listo. Saldo inicial: {banco.minutos_disponibles} min.")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

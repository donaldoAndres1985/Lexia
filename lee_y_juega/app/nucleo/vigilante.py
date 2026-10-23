"""
Proceso vigilante opcional y transparente para Lee y Juega.
Si la aplicación principal se cierra inesperadamente, la vuelve a lanzar.
Puede ser desactivado en cualquier momento desde el Modo Padre.
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

from ..config.configuracion import ConfiguracionSistema, obtener_ruta_datos

logger = logging.getLogger(__name__)


class VigilanteProceso:
    """Supervisa el proceso principal de Lee y Juega."""

    BANDERA_DETENCION = "vigilante_stop.flag"

    @classmethod
    def obtener_ruta_bandera(cls) -> Path:
        return obtener_ruta_datos() / cls.BANDERA_DETENCION

    @classmethod
    def solicitar_parada(cls) -> None:
        """Crea el archivo bandera que indica al vigilante no reiniciar la app."""
        try:
            cls.obtener_ruta_bandera().touch(exist_ok=True)
            logger.info("Bandera de detención de vigilante creada.")
        except Exception as e:
            logger.error(f"Error al crear bandera de vigilante: {e}")

    @classmethod
    def reanudar(cls) -> None:
        """Elimina el archivo bandera para permitir la vigilancia."""
        try:
            ruta = cls.obtener_ruta_bandera()
            if ruta.exists():
                ruta.unlink()
                logger.info("Bandera de detención de vigilante eliminada.")
        except Exception as e:
            logger.error(f"Error al eliminar bandera de vigilante: {e}")

    @classmethod
    def ejecutar_bucle_vigilante(cls, comando_arranque: list[str]) -> None:
        """
        Bucle de vigilancia continuo.
        Se ejecuta como un subproceso visible en el Administrador de tareas.
        """
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [VIGILANTE] %(message)s")
        logger.info("Iniciando servicio vigilante de Lee y Juega...")

        config = ConfiguracionSistema()
        
        while True:
            time.sleep(5)

            # Si el padre desactivó el vigilante o creó la bandera de detención
            if not config.obtener("vigilante_activo", True) or cls.obtener_ruta_bandera().exists():
                logger.info("Vigilante en pausa por solicitud de configuración.")
                continue

            # Verificar si el proceso principal está corriendo
            if not cls._proceso_principal_activo():
                logger.warning("Proceso principal no detectado. Relanzando aplicación...")
                try:
                    subprocess.Popen(comando_arranque, shell=False)
                except Exception as e:
                    logger.error(f"Fallo al relanzar la aplicación: {e}")

    @staticmethod
    def _proceso_principal_activo() -> bool:
        """Determina si Lee y Juega está activo mediante psutil."""
        import psutil
        for proc in psutil.process_iter(["name", "cmdline"]):
            try:
                cmd = " ".join(proc.info.get("cmdline") or [])
                if "lee_y_juega" in cmd or "run.py" in cmd or "LeeYJuega.exe" in (proc.info.get("name") or ""):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False


if __name__ == "__main__":
    # Si se ejecuta directamente como script vigilante
    ruta_main = Path(__file__).resolve().parent.parent / "main.py"
    cmd = [sys.executable, str(ruta_main)]
    VigilanteProceso.ejecutar_bucle_vigilante(cmd)

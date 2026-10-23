"""
Manejo de configuración del sistema Lee y Juega.
Incluye carga, guardado, cifrado de claves con DPAPI y valores por defecto.
"""
from __future__ import annotations

import base64
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Intentar importar win32crypt para DPAPI en Windows
_HAVE_DPAPI = False
try:
    import win32crypt
    _HAVE_DPAPI = True
except ImportError:
    logger.warning("win32crypt no disponible. Usando modo de compatibilidad sin DPAPI nativo.")


def obtener_ruta_datos() -> Path:
    """Retorna el directorio de datos del usuario (%APPDATA%/LeeYJuega o carpeta local)."""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            ruta = Path(appdata) / "LeeYJuega"
            ruta.mkdir(parents=True, exist_ok=True)
            return ruta
    # Fallback para desarrollo o entornos no-Windows
    ruta_local = Path(__file__).resolve().parent.parent.parent.parent / "datos_usuario"
    ruta_local.mkdir(parents=True, exist_ok=True)
    return ruta_local


def cifrar_dpapi(texto_plano: str) -> str:
    """Cifra una cadena usando DPAPI de Windows (CryptProtectData)."""
    if not texto_plano:
        return ""
    datos = texto_plano.encode("utf-8")
    if _HAVE_DPAPI:
        try:
            cifrado = win32crypt.CryptProtectData(datos, "LeeYJuegaSecret", None, None, None, 0)
            return base64.b64encode(cifrado).decode("ascii")
        except Exception as e:
            logger.error(f"Error al cifrar con DPAPI: {e}")
    # En desarrollo/fallback si DPAPI no está disponible
    return "ENC:" + base64.b64encode(datos).decode("ascii")


def descifrar_dpapi(texto_cifrado: str) -> str:
    """Descifra una cadena protegida con DPAPI de Windows."""
    if not texto_cifrado:
        return ""
    if texto_cifrado.startswith("ENC:"):
        # Modo fallback
        try:
            raw = base64.b64decode(texto_cifrado[4:])
            return raw.decode("utf-8")
        except Exception:
            return ""
    if _HAVE_DPAPI:
        try:
            raw = base64.b64decode(texto_cifrado)
            descifrado = win32crypt.CryptUnprotectData(raw, None, None, None, 0)[1]
            return descifrado.decode("utf-8")
        except Exception as e:
            logger.error(f"Error al descifrar con DPAPI: {e}")
            return ""
    return ""


class ConfiguracionSistema:
    """Gestiona la configuración completa de la aplicación."""

    CONFIG_FILE = "configuracion.json"

    def __init__(self, ruta_archivo: Optional[Path] = None):
        self.ruta_archivo = ruta_archivo or (obtener_ruta_datos() / self.CONFIG_FILE)
        self.datos: Dict[str, Any] = self._obtener_valores_por_defecto()
        self.cargar()

    @staticmethod
    def _obtener_valores_por_defecto() -> Dict[str, Any]:
        return {
            # Tiempos y recompensas
            "tiempo_recompensa_min": 60,
            "umbral_aprobacion": 70,  # porcentaje (70%)
            "tiempo_ocio_inicial_min": 0,
            
            # Clasificación de actividad
            "apps_ocio": [
                "RobloxPlayerBeta.exe",
                "RobloxPlayer.exe",
                "Minecraft.Windows.exe",
                "javaw.exe",
                "FortniteClient-Win64-Shipping.exe",
                "Steam.exe",
                "EpicGamesLauncher.exe",
                "GenshinImpact.exe",
                "Valorant.exe",
            ],
            "titulos_ocio": [
                "YouTube",
                "TikTok",
                "Instagram",
                "Facebook",
                "Roblox",
                "Twitch",
                "Netflix",
                "Discord",
                "X / Twitter",
                "Twitter",
                "Disney+",
                "Prime Video",
                "Crunchyroll",
                "AnimeFLV",
                "Poki",
                "Friv",
            ],
            "apps_estudio": [
                "WINWORD.EXE",
                "EXCEL.EXE",
                "POWERPNT.EXE",
                "Code.exe",
                "AcroRd32.exe",
            ],
            "titulos_estudio": [
                "ChatGPT",
                "Gemini",
                "Classroom",
                "Google Docs",
                "Google Sheets",
                "Google Slides",
                "Khan Academy",
                "Wikipedia",
                "Canva",
                "Microsoft Teams",
                "Google Meet",
                "Duolingo",
                "Santillana",
                "Norma",
                "Redalyc",
                "Scielo",
                "EducaPlay",
            ],
            "titulos_musica_permitida": [
                "Spotify",
                "YouTube Music",
                "Deezer",
                "Amazon Music",
            ],

            # Horarios permitidos de ocio (formato HH:MM)
            "horario_ocio_inicio": "08:00",
            "horario_ocio_fin": "21:00",
            "dias_restringidos": [],  # Ejemplo: ["Mon", "Tue"] si aplica franjas especiales

            # Parámetros pedagógicos
            "num_preguntas_por_test": 5,
            "distribucion_preguntas": {
                "literal": 2,
                "inferencial": 2,
                "critico": 1,
            },
            "longitud_palabras_por_nivel": {
                "1": [150, 300],
                "2": [150, 300],
                "3": [300, 500],
                "4": [300, 500],
                "5": [500, 800],
                "6": [500, 800],
            },
            "subir_nivel_consecutivos": 3,
            "subir_nivel_min_puntaje": 85,
            "bajar_nivel_consecutivos": 2,

            # Seguridad e integración
            "clave_padre_hash": "",  # Se asigna en el primer inicio
            "gemini_api_key_cifrada": "",
            "vigilante_activo": True,
            "arrancar_con_windows": True,
            
            # Preferencias visuales
            "tema": "calido",
            "tamano_fuente": "normal",  # "normal", "grande"
        }

    def cargar(self) -> None:
        """Carga la configuración desde el disco o crea la predeterminada."""
        if self.ruta_archivo.exists():
            try:
                with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                    cargados = json.load(f)
                    # Actualización de claves por si hay nuevas versiones
                    for k, v in cargados.items():
                        self.datos[k] = v
                logger.info(f"Configuración cargada desde {self.ruta_archivo}")
            except Exception as e:
                logger.error(f"Error al leer configuración ({e}). Se usarán valores por defecto.")
        else:
            self.guardar()

    def guardar(self) -> None:
        """Guarda la configuración actual en formato JSON."""
        try:
            self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ruta_archivo, "w", encoding="utf-8") as f:
                json.dump(self.datos, f, ensure_ascii=False, indent=2)
            logger.info("Configuración guardada exitosamente.")
        except Exception as e:
            logger.error(f"Error al guardar configuración: {e}")

    def obtener(self, clave: str, default: Any = None) -> Any:
        return self.datos.get(clave, default)

    def establecer(self, clave: str, valor: Any, autoguardar: bool = True) -> None:
        self.datos[clave] = valor
        if autoguardar:
            self.guardar()

    # Helpers específicos
    def establecer_gemini_api_key(self, api_key: str) -> None:
        cifrada = cifrar_dpapi(api_key.strip())
        self.establecer("gemini_api_key_cifrada", cifrada)

    def obtener_gemini_api_key(self) -> str:
        cifrada = self.obtener("gemini_api_key_cifrada", "")
        return descifrar_dpapi(cifrada)

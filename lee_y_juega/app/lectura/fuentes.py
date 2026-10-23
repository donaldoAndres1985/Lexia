"""
Gestor de fuentes de lectura para Lee y Juega.
Integra el banco local offline (mínimo 40 lecturas), Vikidia, Wikipedia,
Wikisource y textos discontinuos generados con Matplotlib.
"""
from __future__ import annotations

import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from .banco_catalogo import asegurar_banco_offline, construir_catalogo_40_lecturas
from .discontinuos import GeneradorTextosDiscontinuos
from .limpieza import FiltroAdecuacionYLimpieza
from ..config.configuracion import obtener_ruta_datos

logger = logging.getLogger(__name__)


class TipoTexto(str, Enum):
    LITERARIO = "literario"
    INFORMATIVO = "informativo"
    DISCONTINUO = "discontinuo"


class GestorFuentesLectura:
    """Administra la recuperación y descarga de textos de diversas fuentes."""

    def __init__(self, ruta_banco: Optional[Path] = None):
        self.ruta_banco = ruta_banco or (obtener_ruta_datos() / "banco_offline")
        self.lecturas_offline: List[Dict[str, Any]] = []
        self.cargar_banco_offline()

    def cargar_banco_offline(self) -> None:
        """Carga en memoria las 40+ lecturas garantizadas del catálogo local."""
        self.lecturas_offline = asegurar_banco_offline(self.ruta_banco)
        logger.info(f"Cargadas {len(self.lecturas_offline)} lecturas offline.")

    def obtener_lecturas_por_nivel(self, nivel: int) -> List[Dict[str, Any]]:
        """Retorna lecturas locales que coinciden con el nivel especificado."""
        coincidencias = [l for l in self.lecturas_offline if l.get("nivel") == nivel]
        if not coincidencias:
            # Si no hay exactas de ese nivel, devolver las más cercanas
            coincidencias = self.lecturas_offline
        return coincidencias

    def obtener_lectura_offline(self, id_lectura: str) -> Optional[Dict[str, Any]]:
        for l in self.lecturas_offline:
            if l.get("id") == id_lectura:
                return l
        return None

    def obtener_texto_discontinuo_generado(self, subtipo: str = "barras") -> Dict[str, Any]:
        """Crea dinámicamente un texto discontinuo con Matplotlib."""
        if subtipo == "tabla":
            return GeneradorTextosDiscontinuos.generar_tabla_consumo_agua()
        return GeneradorTextosDiscontinuos.generar_grafica_barras_biodiversidad()

    # --- FUENTES DE INTERNET ---

    def descargar_vikidia(self, titulo_articulo: str) -> Optional[Dict[str, Any]]:
        """
        Descarga un artículo educativo de Vikidia en español mediante su API pública.
        Vikidia está diseñada específicamente para niños de 8 a 13 años.
        """
        url = "https://es.vikidia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,
            "titles": titulo_articulo,
            "format": "json",
            "redirects": 1,
        }
        try:
            with httpx.Client(timeout=6.0) as client:
                res = client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    pages = data.get("query", {}).get("pages", {})
                    for page_id, page_data in pages.items():
                        if page_id != "-1":
                            extracto = page_data.get("extract", "")
                            limpio = FiltroAdecuacionYLimpieza.limpiar_texto(extracto)
                            aprobado, _ = FiltroAdecuacionYLimpieza.es_apropiado_heuristico(limpio)
                            if aprobado and len(limpio) > 200:
                                return {
                                    "id": f"vikidia_{titulo_articulo.lower()}",
                                    "titulo": page_data.get("title", titulo_articulo),
                                    "tipo_texto": TipoTexto.INFORMATIVO.value,
                                    "subtipo": "enciclopedia_escolar",
                                    "nivel": 2,
                                    "fuente": "Vikidia en español",
                                    "texto": limpio[:2500],
                                    "preguntas": [],  # Las preguntas se generarán con Gemini o respaldo
                                }
        except Exception as e:
            logger.warning(f"No se pudo descargar de Vikidia ({e}). Se usará respaldo offline.")
        return None

    def descargar_wikipedia_escolar(self, titulo_articulo: str) -> Optional[Dict[str, Any]]:
        """Descarga extracto limpio de Wikipedia en español para temas de ciencias o historia."""
        url = "https://es.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,
            "exintro": 1,
            "titles": titulo_articulo,
            "format": "json",
            "redirects": 1,
        }
        try:
            with httpx.Client(timeout=6.0) as client:
                res = client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    pages = data.get("query", {}).get("pages", {})
                    for page_id, page_data in pages.items():
                        if page_id != "-1":
                            extracto = page_data.get("extract", "")
                            limpio = FiltroAdecuacionYLimpieza.limpiar_texto(extracto)
                            aprobado, _ = FiltroAdecuacionYLimpieza.es_apropiado_heuristico(limpio)
                            if aprobado and len(limpio) > 250:
                                return {
                                    "id": f"wiki_{titulo_articulo.lower()}",
                                    "titulo": page_data.get("title", titulo_articulo),
                                    "tipo_texto": TipoTexto.INFORMATIVO.value,
                                    "subtipo": "articulo_informativo",
                                    "nivel": 3,
                                    "fuente": "Wikipedia en español",
                                    "texto": limpio[:2500],
                                    "preguntas": [],
                                }
        except Exception as e:
            logger.warning(f"No se pudo descargar de Wikipedia ({e}). Se usará respaldo offline.")
        return None

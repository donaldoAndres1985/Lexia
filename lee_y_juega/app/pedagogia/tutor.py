"""
Tutor pedagógico interactivo de Lee y Juega.
Ofrece pistas formativas y explicaciones empáticas tras cada respuesta.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TutorPedagogico:
    """Proporciona retroalimentación cercana, explicaciones claras y motivación."""

    @staticmethod
    def obtener_mensaje_acierto(dimension: str) -> str:
        mensajes = {
            "literal": "¡Exacto! Localizaste la pista con total precisión.",
            "inferencial": "¡Brillante deducción! Leíste entre líneas como una profesional.",
            "critico": "¡Excelente ojo crítico! Distinguiste con maestría el argumento central.",
        }
        return mensajes.get(dimension, "¡Muy bien! Respuesta acertada.")

    @staticmethod
    def obtener_explicacion_error(
        enunciado: str,
        opcion_correcta_texto: str,
        opcion_elegida_texto: Optional[str],
        explicacion_pedagogica: str,
        dimension: str,
    ) -> str:
        """Construye un mensaje empático y explicativo para la estudiante."""
        consejo_dimension = {
            "literal": "Recuerda que en las preguntas literales la clave está escrita exactamente en el texto.",
            "inferencial": "Para las inferencias, une las pistas del párrafo como si armaras un rompecabezas.",
            "critico": "En el nivel crítico, pregúntate si es un hecho demostrado o la opinión subjetiva de alguien.",
        }.get(dimension, "")

        texto_respuesta = (
            f"💡 <b>Pista del Tutor:</b><br>"
            f"La respuesta más adecuada es: <b>'{opcion_correcta_texto}'</b>.<br><br>"
            f"<b>¿Por qué?</b> {explicacion_pedagogica}<br><br>"
            f"<i>{consejo_dimension}</i>"
        )
        return texto_respuesta

    @staticmethod
    def generar_resumen_tutor(
        desglose: Dict[str, Dict[str, int]],
        aprobado: bool,
    ) -> str:
        """Analiza en qué área brilló y en cuál requiere más refuerzo."""
        lit = desglose.get("literal", {"aciertos": 0, "total": 0})
        inf = desglose.get("inferencial", {"aciertos": 0, "total": 0})
        crit = desglose.get("critico", {"aciertos": 0, "total": 0})

        lineas = []
        if aprobado:
            lineas.append("🎉 <b>¡Reto superado!</b> Tu esfuerzo y concentración dieron frutos.")
        else:
            lineas.append("💪 <b>¡Buen intento!</b> No te desanimes; cada test es un entrenamiento que fortalece tu cerebro.")

        # Identificar fortalezas
        if lit["total"] > 0 and lit["aciertos"] == lit["total"]:
            lineas.append("• <b>Superpoder detectado:</b> Tu búsqueda de datos literales fue impecable.")
        if inf["total"] > 0 and inf["aciertos"] == inf["total"]:
            lineas.append("• <b>Gran deducción:</b> Tu intuición para leer entre líneas está muy afilada.")
        if crit["total"] > 0 and crit["aciertos"] == crit["total"]:
            lineas.append("• <b>Pensamiento crítico:</b> Evaluaste los argumentos con criterio firme.")

        # Oportunidades de mejora
        if crit["total"] > 0 and crit["aciertos"] < crit["total"]:
            lineas.append("• <b>Oportunidad de práctica:</b> En el siguiente reto, fíjate más si el autor afirma un hecho comprobable o solo da su punto de vista.")
        elif inf["total"] > 0 and inf["aciertos"] < inf["total"]:
            lineas.append("• <b>Oportunidad de práctica:</b> Presta atención a las intenciones ocultas de los personajes.")

        return "<br>".join(lineas)

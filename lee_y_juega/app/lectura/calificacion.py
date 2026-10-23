"""
Evaluador y calificador de pruebas de Lectura Crítica.
Calcula aciertos por dimensión (literal, inferencial, crítico),
porcentaje total, aprobación y retroalimentación motivadora.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EvaluadorTest:
    """Evalúa las respuestas seleccionadas y genera informe pedagógico."""

    def __init__(self, umbral_aprobacion: float = 70.0):
        self.umbral_aprobacion = umbral_aprobacion

    def evaluar(
        self,
        preguntas: List[Dict[str, Any]],
        respuestas_usuario: List[Optional[int]],
    ) -> Dict[str, Any]:
        """
        Compara las respuestas del usuario con las claves correctas.
        Retorna diccionario completo con métricas y retroalimentación.
        """
        total = len(preguntas)
        if total == 0:
            return {
                "total_preguntas": 0,
                "aciertos": 0,
                "puntaje_porcentaje": 0.0,
                "aprobado": False,
                "detalle_preguntas": [],
            }

        aciertos = 0
        desglose = {
            "literal": {"aciertos": 0, "total": 0},
            "inferencial": {"aciertos": 0, "total": 0},
            "critico": {"aciertos": 0, "total": 0},
        }

        detalle_preguntas: List[Dict[str, Any]] = []

        for i, preg in enumerate(preguntas):
            correcta = preg.get("correcta", 0)
            seleccionada = respuestas_usuario[i] if i < len(respuestas_usuario) else None
            es_correcta = (seleccionada == correcta)

            if es_correcta:
                aciertos += 1

            dimension = preg.get("nivel", "literal").lower()
            if dimension not in desglose:
                dimension = "literal"

            desglose[dimension]["total"] += 1
            if es_correcta:
                desglose[dimension]["aciertos"] += 1

            detalle_preguntas.append({
                "indice": i,
                "enunciado": preg.get("enunciado", ""),
                "opciones": preg.get("opciones", []),
                "correcta": correcta,
                "seleccionada": seleccionada,
                "es_correcta": es_correcta,
                "nivel": dimension,
                "explicacion": preg.get("explicacion", ""),
            })

        porcentaje = round((aciertos / total) * 100.0, 1)
        aprobado = porcentaje >= self.umbral_aprobacion

        mensaje_motivador = self._generar_mensaje_motivador(aprobado, porcentaje)

        return {
            "total_preguntas": total,
            "aciertos": aciertos,
            "puntaje_porcentaje": porcentaje,
            "aprobado": aprobado,
            "desglose": desglose,
            "detalle_preguntas": detalle_preguntas,
            "mensaje_motivador": mensaje_motivador,
        }

    @staticmethod
    def _generar_mensaje_motivador(aprobado: bool, porcentaje: float) -> str:
        """Mensaje con tono de entrenador amable y empático."""
        if aprobado:
            if porcentaje == 100:
                return "¡Puntaje perfecto! ¡Demostraste una comprensión brillante! Tus minutos están listos."
            elif porcentaje >= 85:
                return "¡Excelente trabajo! Leíste con mucha atención y superaste el reto con honores."
            else:
                return "¡Muy bien! Aprobaste el test y ganaste tu tiempo de juego. ¡A disfrutar!"
        else:
            if porcentaje >= 50:
                return "¡Estuviste muy cerca! Revisa los consejos del tutor para ver en qué detalle podemos mejorar y lo intentamos de nuevo."
            else:
                return "No te preocupes, cada lectura nos hace más fuertes. Vamos a repasar las pistas y con el siguiente texto lo lograrás."

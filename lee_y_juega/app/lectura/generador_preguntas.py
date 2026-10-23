"""
Generador de preguntas tipo ICFES con Gemini API y respaldo offline garantizado.
Incluye validación estricta de esquema JSON, distribución de dimensiones y claves protegidas.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class GeneradorPreguntas:
    """Genera y valida preguntas de Lectura Crítica (Literal, Inferencial, Crítico)."""

    def __init__(self, configuracion):
        self.config = configuracion

    def generar_preguntas(
        self,
        texto: str,
        titulo: str,
        nivel: int,
        respaldo_preguntas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Intenta generar preguntas usando la API de Gemini.
        Si la API no está configurada, falla o no hay conexión, usa el respaldo offline.
        """
        api_key = self.config.obtener_gemini_api_key()

        if api_key and len(api_key.strip()) > 10:
            preguntas = self._consultar_gemini(texto, titulo, nivel, api_key)
            if preguntas and self._validar_estructura_preguntas(preguntas):
                logger.info(f"Preguntas generadas exitosamente con Gemini ({len(preguntas)} preguntas).")
                return preguntas
            else:
                logger.warning("Fallo al validar preguntas de Gemini. Activando respaldo offline.")

        if respaldo_preguntas and len(respaldo_preguntas) > 0:
            logger.info("Usando banco de preguntas offline pre-curadas.")
            return respaldo_preguntas

        # Si no hay respaldo, generar preguntas sintéticas de emergencia
        return self._generar_preguntas_emergencia(titulo)

    def _consultar_gemini(
        self,
        texto: str,
        titulo: str,
        nivel: int,
        api_key: str,
    ) -> Optional[List[Dict[str, Any]]]:
        """Envía solicitud a la API de Gemini con schema estricto."""
        num_preguntas = int(self.config.obtener("num_preguntas_por_test", 5))

        prompt = f"""
Eres un evaluador experto en la prueba de Lectura Crítica del ICFES para estudiantes de 7.º grado (12 años) en Colombia.
A partir del TEXTO proporcionado, genera exactamente {num_preguntas} preguntas de opción múltiple (4 opciones por pregunta, una sola correcta) en español.

Debes distribuir las preguntas así:
- Nivel literal: 2 preguntas (información explícita, significado directo).
- Nivel inferencial: 2 preguntas (intención del autor, deducción, idea central).
- Nivel crítico: 1 pregunta (distinguir hecho de opinión, supuestos, argumentos).

FORMATO ESTRICTO: Devuelve ÚNICAMENTE un JSON válido con esta lista de objetos:
[
  {{
    "enunciado": "¿Pregunta clara y adecuada?",
    "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
    "correcta": 0,
    "nivel": "literal",
    "explicacion": "Explicación breve de por qué la correcta es la acertada y por qué las demás no."
  }}
]

TÍTULO DEL TEXTO: {titulo}
TEXTO:
{texto[:3000]}
"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }

        try:
            with httpx.Client(timeout=12.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidato = data["candidates"][0]["content"]["parts"][0]["text"]
                    # Limpiar delimitadores markdown si vinieran incluidos
                    candidato_limpio = re.sub(r"^```json\s*", "", candidato.strip(), flags=re.MULTILINE)
                    candidato_limpio = re.sub(r"```$", "", candidato_limpio.strip())
                    
                    parsed = json.loads(candidato_limpio)
                    if isinstance(parsed, list):
                        return parsed
                    elif isinstance(parsed, dict) and "preguntas" in parsed:
                        return parsed["preguntas"]
                else:
                    logger.warning(f"Respuesta no exitosa de Gemini API: {res.status_code} - {res.text[:150]}")
        except Exception as e:
            logger.warning(f"Error de red o procesamiento con Gemini API: {e}")

        return None

    def _validar_estructura_preguntas(self, preguntas: List[Dict[str, Any]]) -> bool:
        """Valida que el JSON cumpla con las especificaciones del test."""
        if not isinstance(preguntas, list) or len(preguntas) < 3:
            return False

        for p in preguntas:
            if not isinstance(p, dict):
                return False
            if not p.get("enunciado") or not isinstance(p.get("opciones"), list):
                return False
            if len(p["opciones"]) != 4:
                return False
            if len(set(p["opciones"])) != 4:  # Opciones no repetidas
                return False
            corr = p.get("correcta")
            if not isinstance(corr, int) or corr < 0 or corr > 3:
                return False
            if p.get("nivel") not in ["literal", "inferencial", "critico"]:
                return False
            if not p.get("explicacion"):
                return False

        return True

    @staticmethod
    def _generar_preguntas_emergencia(titulo: str) -> List[Dict[str, Any]]:
        """Genera preguntas básicas de seguridad si todo lo demás falla."""
        return [
            {
                "enunciado": f"A partir de la lectura de '{titulo}', ¿cuál es el tema principal desarrollado?",
                "opciones": [
                    "El contenido central explicado en los párrafos",
                    "Un tema ajeno a la lectura",
                    "Una lista de compras",
                    "Instrucciones de un juego"
                ],
                "correcta": 0,
                "nivel": "literal",
                "explicacion": "El texto desarrolla las ideas explicadas en sus párrafos principales."
            },
            {
                "enunciado": "¿Qué propósito comunicativo tiene el autor al redactar este texto?",
                "opciones": [
                    "Transmitir información y motivar la reflexión del lector",
                    "Vender un producto comercial",
                    "Confundir con datos erróneos",
                    "Escribir sin ningún objetivo"
                ],
                "correcta": 0,
                "nivel": "inferencial",
                "explicacion": "El texto educativo busca informar y propiciar el análisis comprensivo."
            },
            {
                "enunciado": "¿Cuál de las siguientes afirmaciones constituye una conclusión válida?",
                "opciones": [
                    "La lectura atenta permite comprender mejor el entorno y desarrollar criterio propio",
                    "No es necesario leer los textos para responder preguntas",
                    "Todos los textos dicen exactamente lo mismo",
                    "Las palabras no tienen significado"
                ],
                "correcta": 0,
                "nivel": "critico",
                "explicacion": "Comprender la lectura fortalece el razonamiento y la autonomía intelectual."
            }
        ]

"""
Limpieza de textos y filtro de adecuación para menores (12 años).
Garantiza lecturas sanas, educativas y de longitud adecuada.
"""
from __future__ import annotations

import logging
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Palabras y temáticas no aptas para una niña de 12 años (filtro heurístico inmediato)
PALABRAS_PROHIBIDAS = [
    "asesinato", "masacre", "sangre", "decapitar", "descuartizar", "suicidio",
    "droga", "cocaína", "heroína", "marihuana", "narcotráfico", "narco",
    "sexual", "sexo", "erótico", "pornografía", "desnudo", "prostitución",
    "arma", "pistola", "fusil", "bomba", "terrorismo", "secuestro",
    "odio", "racismo", "tortura", "violación", "abuso", "cadáver", "mutilar",
]


class FiltroAdecuacionYLimpieza:
    """Valida y limpia textos de internet o locales."""

    @staticmethod
    def limpiar_texto(texto_crudo: str) -> str:
        """Elimina etiquetas wiki, saltos múltiples y normaliza espacios."""
        if not texto_crudo:
            return ""

        # Eliminar etiquetas HTML o referencias tipo [1], [editar], etc.
        texto = re.sub(r"<[^>]+>", "", texto_crudo)
        texto = re.sub(r"\[\d+\]", "", texto)
        texto = re.sub(r"\[editar\]", "", texto, flags=re.IGNORECASE)
        texto = re.sub(r"\{\{[^}]+\}\}", "", texto)
        texto = re.sub(r"\s+([.,;:!?])", r"\1", texto)
        texto = re.sub(r"[ \t]+", " ", texto)

        # Normalizar espacios en blanco y saltos de línea repetidos
        lineas = [l.strip() for l in texto.splitlines() if l.strip()]
        texto_limpio = "\n\n".join(lineas)
        return texto_limpio.strip()

    @staticmethod
    def contar_palabras(texto: str) -> int:
        """Cuenta el número de palabras en el texto."""
        palabras = re.findall(r"\b\w+\b", texto)
        return len(palabras)

    @classmethod
    def es_apropiado_heuristico(cls, texto: str) -> Tuple[bool, str]:
        """
        Filtro rápido por lista negra de palabras y patrones peligrosos.
        Retorna (apropiado: bool, razon: str).
        """
        texto_lower = texto.lower()
        for palabra in PALABRAS_PROHIBIDAS:
            patron = rf"\b{palabra}\b"
            if re.search(patron, texto_lower):
                return False, f"Contiene término potencialmente inadecuado: '{palabra}'"
        return True, "Aprobado por filtro heurístico"

    @classmethod
    def validar_longitud(cls, texto: str, nivel: int, rangos_config: Optional[dict] = None) -> Tuple[bool, str]:
        """
        Verifica que el texto esté dentro de los rangos de palabras correspondientes al nivel.
        Nivel 1–2: 150–300 palabras.
        Nivel 3–4: 300–500 palabras.
        Nivel 5–6: 500–800 palabras.
        """
        palabras = cls.contar_palabras(texto)
        rangos_defecto = {
            1: (150, 300),
            2: (150, 300),
            3: (300, 500),
            4: (300, 500),
            5: (500, 800),
            6: (500, 800),
        }
        
        min_p, max_p = rangos_defecto.get(nivel, (150, 400))
        if rangos_config and str(nivel) in rangos_config:
            min_p, max_p = rangos_config[str(nivel)]

        # Margen de tolerancia del 15%
        if palabras < int(min_p * 0.85):
            return False, f"Texto muy corto ({palabras} palabras; mínimo requerido: {min_p})"
        if palabras > int(max_p * 1.25):
            return False, f"Texto muy largo ({palabras} palabras; máximo recomendado: {max_p})"

        return True, f"Longitud adecuada ({palabras} palabras)"

    @classmethod
    def validar_adecuacion_gemini(cls, texto: str, gemini_cliente) -> Tuple[bool, str]:
        """
        Verificación semántica usando Gemini:
        '¿Es este texto apropiado para una niña de 12 años? Responde solo sí/no y por qué.'
        """
        if not gemini_cliente:
            # Si no hay cliente Gemini, confiar en el filtro heurístico
            return cls.es_apropiado_heuristico(texto)

        prompt = (
            "Eres un tutor educativo infantil y filtro de seguridad para niños de 12 años (7.º grado en Colombia).\n"
            "Analiza el siguiente texto y responde ESTRICTAMENTE en este formato JSON:\n"
            "{\"apropiado\": true/false, \"motivo\": \"explicación breve\"}\n"
            "Considera inapropiado: violencia explícita, contenido sexual, drogas, terror, discriminación o temas para adultos.\n\n"
            f"TEXTO A EVALUAR:\n{texto[:1500]}"
        )

        try:
            respuesta_json = gemini_cliente.generar_json(prompt)
            if respuesta_json and "apropiado" in respuesta_json:
                return bool(respuesta_json["apropiado"]), respuesta_json.get("motivo", "")
        except Exception as e:
            logger.warning(f"Error al verificar adecuación con Gemini ({e}). Usando filtro heurístico.")

        return cls.es_apropiado_heuristico(texto)

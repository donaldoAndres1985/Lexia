"""
Diccionario y Glosario Contextual ICFES para estudiantes de 7.º grado.
Permite consultar definiciones, sinónimos y ejemplos amigables para 12 años
al hacer doble clic sobre cualquier palabra de la lectura.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

# Glosario especializado de términos frecuentes en pruebas de Lectura Crítica del ICFES
GLOSARIO_ICFES: Dict[str, Dict[str, str]] = {
    "efimero": {
        "definicion": "Que dura muy poco tiempo, fugaz o pasajero.",
        "sinonimos": "Breve, pasajero, fugaz, momentáneo.",
        "ejemplo": "La belleza de esa flor fue efímera; marchitó al llegar la tarde."
    },
    "verosimil": {
        "definicion": "Que tiene apariencia de ser verdadero, creíble o lógico.",
        "sinonimos": "Creíble, plausible, probable, lógico.",
        "ejemplo": "Aunque era un cuento de misterio, su explicación resultaba verosímil."
    },
    "inverosimil": {
        "definicion": "Que parece imposible o muy difícil de creer.",
        "sinonimos": "Increíble, absurdo, fantástico, descabellado.",
        "ejemplo": "Contó una historia inverosímil sobre dragones en la escuela."
    },
    "sesgo": {
        "definicion": "Inclinación o preferencia hacia una idea que impide juzgar con neutralidad.",
        "sinonimos": "Prejuicio, inclinación, parcialidad.",
        "ejemplo": "Ese artículo periodístico tenía un sesgo a favor del equipo local."
    },
    "premisa": {
        "definicion": "Idea o hecho de partida que sirve como base para llegar a una conclusión.",
        "sinonimos": "Supuesto, punto de partida, hipótesis.",
        "ejemplo": "Partiendo de la premisa de que todos respiramos aire, debemos cuidar los bosques."
    },
    "refutar": {
        "definicion": "Demostrar que una afirmación o argumento es falso usando razones y pruebas.",
        "sinonimos": "Contradecir, rebatir, desmentir, objetar.",
        "ejemplo": "La científica refutó la teoría presentando mediciones exactas del laboratorio."
    },
    "implicito": {
        "definicion": "Que está incluido o sugerido en el texto sin estar dicho con palabras directas (se lee entre líneas).",
        "sinonimos": "Tácito, sobreentendido, insinuado.",
        "ejemplo": "Aunque no dijo que estaba enfadado, su tono de voz lo dejaba implícito."
    },
    "explicito": {
        "definicion": "Que está dicho de forma clara, directa y visible, sin dejar lugar a dudas.",
        "sinonimos": "Claro, directo, manifiesto, evidente.",
        "ejemplo": "La regla era explícita: prohibido correr en los pasillos."
    },
    "discrepancia": {
        "definicion": "Diferencia de opinión, desacuerdo o contradicción entre dos personas o datos.",
        "sinonimos": "Desacuerdo, diferencia, divergencia, disputa.",
        "ejemplo": "Hubo una ligera discrepancia entre los dos testigos sobre la hora del suceso."
    },
    "conjetura": {
        "definicion": "Juicio o suposición formado a partir de indicios o pistas incompletas.",
        "sinonimos": "Sospecha, suposición, hipótesis, presunción.",
        "ejemplo": "Sin pruebas definitivas, la policía solo podía hacer conjeturas."
    },
    "simbiosis": {
        "definicion": "Asociación íntima y de ayuda mutua entre dos seres vivos de distinta especie.",
        "sinonimos": "Cooperación mutua, alianza biológica.",
        "ejemplo": "El alga y el coral viven en una simbiosis indispensable para el arrecife."
    },
    "obsolescencia": {
        "definicion": "Condición de un objeto que se vuelve viejo o inservible por el paso del tiempo o por la aparición de modelos más nuevos.",
        "sinonimos": "Desuso, caducidad, envejecimiento técnico.",
        "ejemplo": "La obsolescencia programada hace que algunas baterías duren poco tiempo."
    },
    "subjetivo": {
        "definicion": "Que depende de los sentimientos, gustos o puntos de vista personales de cada quien.",
        "sinonimos": "Personal, opinable, individual.",
        "ejemplo": "Decir que el helado de fresa es el más rico es un juicio completamente subjetivo."
    },
    "objetivo": {
        "definicion": "Que se basa en hechos reales, medibles y comprobables, sin dejarse llevar por emociones.",
        "sinonimos": "Neutral, imparcial, científico, medible.",
        "ejemplo": "El termómetro arrojó un dato objetivo: la temperatura era de 38 grados."
    },
    "vehemente": {
        "definicion": "Que se hace con mucha fuerza, pasión, ímpetu o energía ardiente.",
        "sinonimos": "Apasionado, intenso, fogoso, enérgico.",
        "ejemplo": "El líder estudiantil dio un discurso vehemente en defensa de la biblioteca."
    },
    "apacible": {
        "definicion": "Tranquilo, sereno, agradable y libre de ruidos molestos.",
        "sinonimos": "Calmado, sereno, sosegado, pacífico.",
        "ejemplo": "Pasaron una tarde apacible leyendo bajo la sombra del guayacán."
    },
    "desden": {
        "definicion": "Actitud de desprecio o indiferencia hacia alguien o algo.",
        "sinonimos": "Desprecio, indiferencia, menosprecio.",
        "ejemplo": "La zorra miró las uvas con desdén cuando no pudo alcanzarlas."
    },
    "proposito": {
        "definicion": "La intención, objetivo o meta que persigue un autor al escribir un texto.",
        "sinonimos": "Intención, meta, finalidad, objetivo.",
        "ejemplo": "El propósito del afiche era convencer a los vecinos de no arrojar basura al río."
    },
    "tesis": {
        "definicion": "La postura, opinión central o afirmación principal que defiende el autor a lo largo de su texto.",
        "sinonimos": "Postura, afirmación central, propuesta.",
        "ejemplo": "La tesis del autor es que la lectura diaria transforma el cerebro humano."
    },
    "argumento": {
        "definicion": "Razonamiento, prueba o dato que se emplea para demostrar que una afirmación es verdadera o falsa.",
        "sinonimos": "Razón, prueba, justificación, fundamento.",
        "ejemplo": "Presentó como argumento las estadísticas de deforestación del último año."
    }
}


class GlosarioContextual:
    """Procesa consultas léxicas para enriquecer la lectura activa."""

    @staticmethod
    def limpiar_termino(palabra: str) -> str:
        """Limpia signos de puntuación, tildes y caracteres especiales para búsqueda."""
        palabra_limpia = re.sub(r"[^\w\sáéíóúüñÁÉÍÓÚÜÑ]", "", palabra.lower().strip())
        # Quitar tildes para índice robusto
        reemplazos = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ü", "u"))
        for a, b in reemplazos:
            palabra_limpia = palabra_limpia.replace(a, b)
        return palabra_limpia

    @classmethod
    def buscar(cls, palabra: str) -> Optional[Dict[str, str]]:
        """Busca el término en el glosario especializado."""
        if not palabra:
            return None

        clave = cls.limpiar_termino(palabra)

        # 1. Búsqueda directa
        if clave in GLOSARIO_ICFES:
            res = GLOSARIO_ICFES[clave].copy()
            res["palabra"] = palabra.capitalize()
            return res

        # 2. Búsqueda por coincidencia parcial (lematización simple)
        for k, v in GLOSARIO_ICFES.items():
            if k in clave or clave in k:
                res = v.copy()
                res["palabra"] = palabra.capitalize()
                return res

        # 3. Explicación contextual de cortesía si es palabra común
        return {
            "palabra": palabra.capitalize(),
            "definicion": f"Palabra leída en el texto: '{palabra}'. Revisa el contexto de la oración para deducir su significado.",
            "sinonimos": "Pregúntale al tutor o fíjate en las palabras que la acompañan.",
            "ejemplo": "En la lectura actual cumple una función para dar sentido a la idea del párrafo."
        }

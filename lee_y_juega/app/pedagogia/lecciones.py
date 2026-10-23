"""
Lecciones interactivas para enseñar antes de exigir.
Cubre las tres dimensiones del ICFES:
1. Nivel Literal: 'Leer lo que dice el texto'
2. Nivel Inferencial: 'Leer entre líneas'
3. Nivel Crítico: 'Leer con ojo crítico'
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ContenidoLeccion:
    """Estructura de contenidos para cada lección interactiva."""

    @staticmethod
    def obtener_leccion_literal() -> Dict[str, Any]:
        return {
            "tipo": "literal",
            "titulo": "Lección 1: Leer lo que dice el texto (Comprensión Literal)",
            "introduccion": (
                "¡Hola! Antes de empezar, vamos a descubrir el primer gran superpoder de la lectura: "
                "la <b>Comprensión Literal</b>.<br><br>"
                "Comprender de forma literal significa <b>encontrar información que está escrita de forma directa y visible</b> en el texto, "
                "sin inventar ni adivinar nada. Es como ser una detective que busca pistas con lupa."
            ),
            "ejemplo": {
                "texto_ejemplo": (
                    "Camila salió temprano hacia el colegio llevando un paraguas rojo brillante porque el cielo estaba completamente nublado."
                ),
                "explicacion_paso_a_paso": (
                    "• <b>¿Qué llevaba Camila?</b> Si miramos el texto resaltado, dice exactamente: <i>un paraguas rojo brillante</i>.<br>"
                    "• <b>¿Por qué?</b> El texto dice: <i>porque el cielo estaba completamente nublado</i>.<br><br>"
                    "¡Así de fácil! Las respuestas literales están esperando directamente en las palabras del autor."
                )
            },
            "consejos": [
                "Vuelve a leer el párrafo con calma: la respuesta está ahí con palabras exactas o muy parecidas.",
                "Subraya mentalmente nombres, fechas, lugares, colores y cantidades.",
                "No te dejes engañar por opciones que suenen bonitas pero que el texto nunca mencionó."
            ],
            "mini_practica": [
                {
                    "enunciado": "En la frase 'Mateo adoptó un perro de color caramelo llamado Toby en el parque': ¿Cómo se llama el perro?",
                    "opciones": ["Mateo", "Toby", "Caramelo", "Parque"],
                    "correcta": 1,
                    "pista": "Busca la palabra que sigue inmediatamente después de 'llamado'."
                },
                {
                    "enunciado": "¿De qué color era el perro de Mateo según la frase?",
                    "opciones": ["Negro azabache", "Blanco con manchas", "Color caramelo", "Gris ceniza"],
                    "correcta": 2,
                    "pista": "Fíjate en las palabras que describen el pelaje del animal."
                }
            ]
        }

    @staticmethod
    def obtener_leccion_inferencial() -> Dict[str, Any]:
        return {
            "tipo": "inferencial",
            "titulo": "Lección 2: Leer entre líneas (Comprensión Inferencial)",
            "introduccion": (
                "¡Bienvenida al segundo nivel! Ahora aprenderemos a <b>Leer entre líneas</b>.<br><br>"
                "A veces, los autores no te dicen todo masticado. Te dan <b>pistas</b> para que tú, "
                "usando tu inteligencia y tu experiencia, deduzcas lo que está pasando o lo que el personaje siente."
            ),
            "ejemplo": {
                "texto_ejemplo": (
                    "Sebastián entró a la sala tiritando, con los labios morados y los zapatos dejando huellas de agua en la alfombra."
                ),
                "explicacion_paso_a_paso": (
                    "• El texto <b>no dice</b> 'estaba lloviendo y hacía frío'.<br>"
                    "• Pero al unir las pistas (tiritar + labios morados + zapatos con agua), tú <b>deduces con certeza</b> "
                    "que Sebastián se mojó bajo un aguacero muy frío."
                )
            },
            "consejos": [
                "Pregúntate: ¿Qué significa este detalle? ¿Qué me quiere decir el autor sin decirlo directamente?",
                "Para la <b>idea principal</b>: pregúntate de qué trata casi todo el texto en una sola frase.",
                "Identifica las emociones de los personajes por la forma en que actúan o respiran."
            ],
            "mini_practica": [
                {
                    "enunciado": "Si lees: 'Laura guardó su toalla, se puso bloqueador y escuchó el romper de las olas', ¿dónde está Laura?",
                    "opciones": ["En el cine", "En una biblioteca", "En la playa", "En un nevado"],
                    "correcta": 2,
                    "pista": "Revisa los elementos: toalla, protector solar y olas de mar."
                },
                {
                    "enunciado": "Si un personaje 'aprieta los puños y respira agitado tras escuchar una noticia', probablemente siente:",
                    "opciones": ["Sueño y cansancio", "Enojo o indignación", "Mucha hambre", "Aburrimiento total"],
                    "correcta": 1,
                    "pista": "Apretar los puños con respiración fuerte es la reacción típica de la molestia o la furia."
                }
            ]
        }

    @staticmethod
    def obtener_leccion_critico() -> Dict[str, Any]:
        return {
            "tipo": "critico",
            "titulo": "Lección 3: Leer con ojo crítico (Comprensión Crítica)",
            "introduccion": (
                "¡Llegaste al nivel de las personas expertas! <b>Leer con ojo crítico</b> significa que tú no te "
                "tragas todo lo que lees sin pensarlo. Tú dialogas con el texto y evalúas si lo que dice es verdad, si es una opinión o si tiene un sesgo.<br><br>"
                "En la prueba del ICFES, esta es la habilidad reina: te pedirán distinguir un <b>hecho</b> de una <b>opinión</b>, "
                "detectar supuestos y saber qué argumento es fuerte o débil."
            ),
            "ejemplo": {
                "texto_ejemplo": (
                    "<b>Hecho (Dato comprobable):</b> Colombia cuenta con más de 1.900 especies de aves registradas en su territorio.<br>"
                    "<b>Opinión (Juicio de valor personal):</b> Las aves de Colombia son las más hermosas y alegres de toda la Tierra."
                ),
                "explicacion_paso_a_paso": (
                    "• El <b>hecho</b> se puede contar, medir y comprobar científicamente.<br>"
                    "• La <b>opinión</b> depende de los gustos de cada persona: para alguien otras aves pueden ser más hermosas."
                )
            },
            "consejos": [
                "Fíjate en palabras valorativas como 'maravilloso', 'el mejor', 'el peor', 'horrible': suelen señalar opiniones.",
                "Pregúntate: ¿Qué pruebas o datos presenta el autor para sostener lo que dice?",
                "Recuerda que una persona puede estar en desacuerdo con una opinión con todo respeto, usando argumentos sólidos."
            ],
            "mini_practica": [
                {
                    "enunciado": "¿Cuál de los siguientes enunciados es un HECHO comprobable y no una opinión?",
                    "opciones": [
                        "El chocolate es el postre más delicioso del universo.",
                        "El agua hierve a 100 grados Celsius a nivel del mar.",
                        "Los gatos son mucho más simpáticos que los perros.",
                        "La música clásica es la única que vale la pena escuchar."
                    ],
                    "correcta": 1,
                    "pista": "Busca la afirmación que se pueda medir en un laboratorio científico."
                },
                {
                    "enunciado": "¿Qué argumento debilitaría la afirmación: 'Todos los jóvenes usan gafas porque leen mucho'?",
                    "opciones": [
                        "Que las gafas tienen marcos de diferentes colores.",
                        "Mostrar que muchos jóvenes usan gafas por herencia genética o por mirar pantallas de celular.",
                        "Decir que leer libros es muy entretenido.",
                        "Que las ópticas venden lentes de contacto."
                    ],
                    "correcta": 1,
                    "pista": "Un contraargumento demuestra otras causas distintas a la planteada por el autor."
                }
            ]
        }


class GestorLecciones:
    """Administra la entrega de lecciones pedagógicas según el historial."""

    def __init__(self, repositorio):
        self.repo = repositorio

    def debe_mostrar_leccion(self, tipo_lectura: str) -> bool:
        """Determina si la niña nunca ha tomado la lección interactiva de este tipo."""
        return not self.repo.ha_completado_leccion(tipo_lectura)

    def obtener_contenido_leccion(self, tipo_lectura: str) -> Dict[str, Any]:
        if tipo_lectura == "literal":
            return ContenidoLeccion.obtener_leccion_literal()
        elif tipo_lectura == "inferencial":
            return ContenidoLeccion.obtener_leccion_inferencial()
        else:
            return ContenidoLeccion.obtener_leccion_critico()

    def marcar_completada(self, tipo_lectura: str) -> None:
        self.repo.marcar_leccion_completada(tipo_lectura)
        logger.info(f"Lección interactiva '{tipo_lectura}' completada y registrada.")

"""
Generador de textos discontinuos (gráficas, tablas, infografías) con Matplotlib.
Diseñado para la evaluación de Lectura Crítica del ICFES en 7.º grado.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")  # Backend no interactivo para Qt/hilos seguros
import matplotlib.pyplot as plt

from ..config.configuracion import obtener_ruta_datos

logger = logging.getLogger(__name__)


class GeneradorTextosDiscontinuos:
    """Crea imágenes de textos discontinuos temáticos apropiados para Colombia y 7.º grado."""

    @staticmethod
    def _obtener_carpeta_graficas() -> Path:
        carpeta = obtener_ruta_datos() / "graficas_generadas"
        carpeta.mkdir(parents=True, exist_ok=True)
        return carpeta

    @classmethod
    def generar_grafica_barras_biodiversidad(cls) -> Dict[str, Any]:
        """Gráfica de especies de aves por regiones naturales de Colombia."""
        regiones = ["Andina", "Amazonía", "Pacífica", "Caribe", "Orinoquía"]
        especies = [974, 750, 650, 480, 420]
        colores = ["#4CAF50", "#2E7D32", "#00897B", "#F57C00", "#FFB300"]

        fig, ax = plt.subplots(figsize=(7, 4.2), dpi=100)
        barras = ax.bar(regiones, especies, color=colores, edgecolor="#333333", width=0.6)

        ax.set_title("Especies de Aves Registradas por Región Natural en Colombia", fontsize=12, fontweight="bold", pad=12)
        ax.set_ylabel("Número estimado de especies", fontsize=10)
        ax.set_xlabel("Regiones Naturales", fontsize=10)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        # Añadir valores numéricos sobre cada barra
        for barra in barras:
            altura = barra.get_height()
            ax.annotate(f"{altura}",
                        xy=(barra.get_x() + barra.get_width() / 2, altura),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=9, fontweight="bold")

        plt.tight_layout()
        ruta_img = cls._obtener_carpeta_graficas() / "biodiversidad_colombia.png"
        fig.savefig(ruta_img, format="png")
        plt.close(fig)

        return {
            "titulo": "Biodiversidad: Las Aves de Colombia por Región",
            "tipo_texto": "discontinuo",
            "subtipo": "grafica_barras",
            "nivel": 2,
            "ruta_imagen": str(ruta_img),
            "texto_contexto": (
                "Colombia es el país con mayor diversidad de aves en el planeta, superando las 1.900 especies. "
                "La gráfica muestra cómo se distribuyen estas especies en sus cinco regiones naturales principales. "
                "La cordillera de los Andes ofrece múltiples pisos térmicos, lo que favorece una enorme variedad de hábitats."
            ),
            "preguntas": [
                {
                    "enunciado": "¿Cuál es la región natural con el mayor número de especies de aves según la gráfica?",
                    "opciones": ["La región Pacífica", "La región Andina", "La región Amazonía", "La región Caribe"],
                    "correcta": 1,
                    "nivel": "literal",
                    "explicacion": "La barra más alta corresponde a la región Andina con 974 especies."
                },
                {
                    "enunciado": "A partir de la gráfica y el texto, ¿por qué la región Andina concentra tantas especies?",
                    "opciones": [
                        "Porque es la única región que tiene ríos caudalosos.",
                        "Porque sus diversos pisos térmicos generan múltiples hábitats favorables.",
                        "Porque las aves migran allí para escapar del invierno del Caribe.",
                        "Porque la Amazonía no cuenta con árboles suficientes para las aves."
                    ],
                    "correcta": 1,
                    "nivel": "inferencial",
                    "explicacion": "El texto explica explícitamente que los pisos térmicos de los Andes favorecen la variedad de hábitats."
                },
                {
                    "enunciado": "Si una campaña ambiental busca proteger la región con menor cantidad registrada en esta gráfica, ¿en cuál debería enfocarse?",
                    "opciones": ["En la Orinoquía", "En el Caribe", "En la Amazonía", "En la región Andina"],
                    "correcta": 0,
                    "nivel": "inferencial",
                    "explicacion": "La Orinoquía tiene la cifra más baja (420 especies registradas en esta muestra)."
                },
                {
                    "enunciado": "¿Qué propósito comunicativo principal tiene el autor al utilizar una gráfica de barras en lugar de solo un párrafo?",
                    "opciones": [
                        "Ocultar que Colombia tiene menos aves que otros países vecinos.",
                        "Permitir al lector comparar de forma rápida y visual las cantidades entre regiones.",
                        "Hacer que el texto parezca un examen difícil de matemáticas.",
                        "Demostrar que la región del Caribe no necesita cuidado ambiental."
                    ],
                    "correcta": 1,
                    "nivel": "critico",
                    "explicacion": "Las gráficas de barras se emplean para facilitar la comparación visual directa de magnitudes."
                },
                {
                    "enunciado": "¿Cuál de las siguientes afirmaciones es una opinión y NO un dato comprobable en la gráfica?",
                    "opciones": [
                        "La región Andina tiene más de 900 especies registradas.",
                        "Las aves de la región Pacífica son las más hermosas y alegres de Colombia.",
                        "La Amazonía supera a la región Caribe en número de especies.",
                        "El total de especies en Colombia supera las 1.900 según el texto."
                    ],
                    "correcta": 1,
                    "nivel": "critico",
                    "explicacion": "Calificar a las aves como 'las más hermosas y alegres' es un juicio de valor subjetivo (opinión), no un dato medible."
                }
            ]
        }

    @classmethod
    def generar_tabla_consumo_agua(cls) -> Dict[str, Any]:
        """Tabla comparativa de consumo responsable de agua en el hogar."""
        fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=100)
        ax.axis("off")

        columnas = ["Actividad Cotidiana", "Consumo Tradicional", "Consumo Ahorrador", "Ahorro Estimado"]
        filas = [
            ["Ducha de 10 minutos", "120 Litros", "45 Litros (5 min con cabezal eficiente)", "62.5 %"],
            ["Lavado de dientes con grifo abierto", "15 Litros", "1 Litro (usando un vaso con agua)", "93.3 %"],
            ["Lavado de platos a mano continuo", "80 Litros", "25 Litros (usando tina de remojo)", "68.7 %"],
            ["Lavadora carga completa vs media carga", "100 Litros (2 medias)", "60 Litros (1 carga completa)", "40.0 %"],
        ]

        tabla = ax.table(
            cellText=filas,
            colLabels=columnas,
            loc="center",
            cellLoc="center",
        )
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(9)
        tabla.scale(1.1, 1.8)

        # Estilo de encabezado
        for col_idx in range(len(columnas)):
            cell = tabla[(0, col_idx)]
            cell.set_facecolor("#1976D2")
            cell.get_text().set_color("white")
            cell.get_text().set_weight("bold")

        plt.title("Guía Práctica: Ahorro de Agua en el Hogar (MinAmbiente)", fontsize=11, fontweight="bold", pad=15)
        plt.tight_layout()

        ruta_img = cls._obtener_carpeta_graficas() / "consumo_agua_hogar.png"
        fig.savefig(ruta_img, format="png")
        plt.close(fig)

        return {
            "titulo": "Uso Eficiente del Agua: Tabla Comparativa del Hogar",
            "tipo_texto": "discontinuo",
            "subtipo": "tabla",
            "nivel": 3,
            "ruta_imagen": str(ruta_img),
            "texto_contexto": (
                "El cuidado de los recursos hídricos es fundamental en Colombia. "
                "Pequeñas modificaciones en las rutinas diarias pueden reducir drásticamente el consumo de agua potable. "
                "Revisa con atención los datos de la tabla antes de contestar las preguntas."
            ),
            "preguntas": [
                {
                    "enunciado": "Según la tabla, ¿cuántos litros de agua se gastan al lavarse los dientes con el grifo abierto?",
                    "opciones": ["1 Litro", "15 Litros", "45 Litros", "80 Litros"],
                    "correcta": 1,
                    "nivel": "literal",
                    "explicacion": "La fila de lavado de dientes indica exactamente 15 litros en consumo tradicional."
                },
                {
                    "enunciado": "¿Cuál de las actividades presenta el mayor porcentaje de ahorro estimado al implementar la medida ecológica?",
                    "opciones": ["Ducha de 10 minutos", "Lavado de platos a mano", "Lavado de dientes con vaso", "Lavadora con carga completa"],
                    "correcta": 2,
                    "nivel": "inferencial",
                    "explicacion": "El lavado de dientes con un vaso alcanza un 93.3% de ahorro, el porcentaje más alto de la tabla."
                },
                {
                    "enunciado": "Si una familia de 4 personas se ducha una vez al día con la medida ahorradora en vez de la tradicional, ¿cuántos litros ahorran al día?",
                    "opciones": ["75 litros", "150 litros", "300 litros", "480 litros"],
                    "correcta": 2,
                    "nivel": "inferencial",
                    "explicacion": "Cada persona ahorra (120 - 45) = 75 litros. En 4 personas: 75 * 4 = 300 litros diarios."
                },
                {
                    "enunciado": "¿Qué supuesto da por sentado el autor de esta tabla para afirmar que se ahorra agua?",
                    "opciones": [
                        "Que todas las personas tienen suficiente dinero para comprar lavavajillas automáticos.",
                        "Que las personas tienen la voluntad de cambiar sus hábitos diarios cuando conocen los datos.",
                        "Que el agua potable pronto va a desaparecer por completo en todo el país.",
                        "Que ducharse 5 minutos es perjudicial para la higiene de los jóvenes."
                    ],
                    "correcta": 1,
                    "nivel": "critico",
                    "explicacion": "La tabla asume el supuesto pedagógico de que la información motiva cambios de conducta voluntaria en las personas."
                },
                {
                    "enunciado": "¿Qué argumento debilitaría más la conclusión de que ducharse 5 minutos siempre ahorra agua?",
                    "opciones": [
                        "Que una persona use una manguera de alta presión en esos 5 minutos que gaste más de 150 litros.",
                        "Que el agua fría despierte más a las personas por la mañana.",
                        "Que el champú biodegradable cueste más en el supermercado.",
                        "Que en invierno las personas prefieran duchas calientes."
                    ],
                    "correcta": 0,
                    "nivel": "critico",
                    "explicacion": "Si el caudal en esos 5 minutos supera los 150 litros debido a una manguera de alta presión, el ahorro previsto no se cumpliría."
                }
            ]
        }

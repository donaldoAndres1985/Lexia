"""
Gestor del Mini-Simulacro Formal ICFES Saber 7.° para Lee y Juega.
Estructura una prueba diagnóstica de 15 preguntas con temporizador general,
cálculo de escala oficial (0-100) y clasificación por niveles de desempeño.
"""
from __future__ import annotations

import logging
import random
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GestorSimulacro:
    """Organiza y evalúa simulacros completos de Lectura Crítica."""

    DURACION_MINUTOS = 25  # 25 minutos para 15 preguntas
    TOTAL_PREGUNTAS = 15

    def __init__(self, gestor_fuentes, repositorio):
        self.fuentes = gestor_fuentes
        self.repo = repositorio

    def generar_simulacro_15_preguntas(self) -> Dict[str, Any]:
        """
        Ensambla un cuadernillo equilibrado con 3 textos variados:
        - 1 Texto Literario (5 preguntas)
        - 1 Texto Informativo (5 preguntas)
        - 1 Texto Discontinuo (5 preguntas)
        Total: 15 preguntas cubriendo Literal, Inferencial y Crítico.
        """
        lecturas = self.fuentes.lecturas_offline

        literarios = [l for l in lecturas if l.get("tipo_texto") == "literario" and len(l.get("preguntas", [])) >= 5]
        informativos = [l for l in lecturas if l.get("tipo_texto") == "informativo" and len(l.get("preguntas", [])) >= 5]
        discontinuos = [l for l in lecturas if l.get("tipo_texto") == "discontinuo" and len(l.get("preguntas", [])) >= 5]

        t_lit = random.choice(literarios) if literarios else lecturas[0]
        t_inf = random.choice(informativos) if informativos else lecturas[1]
        t_disc = random.choice(discontinuos) if discontinuos else lecturas[2]

        bloques = [
            {"lectura": t_lit, "preguntas": t_lit["preguntas"][:5]},
            {"lectura": t_inf, "preguntas": t_inf["preguntas"][:5]},
            {"lectura": t_disc, "preguntas": t_disc["preguntas"][:5]},
        ]

        preguntas_planas = []
        for b_idx, bloque in enumerate(bloques):
            for p in bloque["preguntas"]:
                item = p.copy()
                item["titulo_lectura"] = bloque["lectura"]["titulo"]
                item["tipo_texto"] = bloque["lectura"]["tipo_texto"]
                preguntas_planas.append(item)

        return {
            "titulo": "Mini-Simulacro Oficial ICFES Saber 7.°",
            "duracion_segundos": self.DURACION_MINUTOS * 60,
            "bloques": bloques,
            "preguntas": preguntas_planas,
        }

    def calificar_simulacro(
        self,
        preguntas: List[Dict[str, Any]],
        respuestas_usuario: List[Optional[int]],
        tiempo_empleado_segundos: int,
    ) -> Dict[str, Any]:
        """
        Evalúa el simulacro y asigna el nivel de desempeño del ICFES:
        - Insuficiente: 0 a 54 puntos
        - Mínimo: 55 a 70 puntos
        - Satisfactorio: 71 a 85 puntos
        - Avanzado: 86 a 100 puntos
        """
        total = len(preguntas)
        aciertos = 0
        aciertos_por_dimension = {"literal": 0, "inferencial": 0, "critico": 0}
        total_por_dimension = {"literal": 0, "inferencial": 0, "critico": 0}

        for i, preg in enumerate(preguntas):
            dim = preg.get("nivel", "literal").lower()
            if dim not in total_por_dimension:
                dim = "literal"
            total_por_dimension[dim] += 1

            seleccionada = respuestas_usuario[i] if i < len(respuestas_usuario) else None
            if seleccionada == preg.get("correcta", 0):
                aciertos += 1
                aciertos_por_dimension[dim] += 1

        puntaje_global = round((aciertos / total) * 100.0, 1) if total > 0 else 0.0

        if puntaje_global >= 86.0:
            nivel = "Avanzado"
            diag = (
                "¡Excelente desempeño! Demuestras una comprensión crítica madura, distingues tesis de argumentos "
                "y evalúas la solidez de los textos con gran perspicacia."
            )
        elif puntaje_global >= 71.0:
            nivel = "Satisfactorio"
            diag = (
                "¡Nivel Satisfactorio alcanzado! Comprendes las ideas globales y deduces intenciones con seguridad. "
                "Para llegar a nivel Avanzado, continúa practicando la detección de supuestos y opiniones sutiles."
            )
        elif puntaje_global >= 55.0:
            nivel = "Mínimo"
            diag = (
                "Nivel Mínimo consolidado. Identificas muy bien los datos explícitos del texto. Te recomendamos "
                "repasar la lección de 'Leer entre líneas' para fortalecer las inferencias."
            )
        else:
            nivel = "Insuficiente"
            diag = (
                "Buen punto de partida para entrenar. Vamos a enfocar los esfuerzos en releer despacio los párrafos "
                "para ubicar los datos explícitos antes de responder."
            )

        # Guardar en base de datos
        sim_id = self.repo.guardar_simulacro_resultado(
            puntaje_global=puntaje_global,
            nivel_desempeno=nivel,
            total_preguntas=total,
            aciertos=aciertos,
            tiempo_empleado_segundos=tiempo_empleado_segundos,
            diagnostico_texto=diag,
        )

        return {
            "id": sim_id,
            "puntaje_global": puntaje_global,
            "nivel_desempeno": nivel,
            "aciertos": aciertos,
            "total_preguntas": total,
            "tiempo_minutos": round(tiempo_empleado_segundos / 60, 1),
            "diagnostico": diag,
            "desglose_dimensiones": {
                "literal": f"{aciertos_por_dimension['literal']}/{total_por_dimension['literal']}",
                "inferencial": f"{aciertos_por_dimension['inferencial']}/{total_por_dimension['inferencial']}",
                "critico": f"{aciertos_por_dimension['critico']}/{total_por_dimension['critico']}",
            }
        }

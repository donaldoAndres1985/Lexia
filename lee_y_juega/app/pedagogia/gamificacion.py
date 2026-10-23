"""
Sistema de Gamificación Positiva para Lee y Juega.
Gestiona el desbloqueo de insignias, la evolución de Koko el Colibrí
y la Ruleta de Bonificación al lograr el 100% de aciertos.
"""
from __future__ import annotations

import logging
import random
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class GestorGamificacion:
    """Supervisa el progreso lúdico, logros y recompensas por mérito."""

    def __init__(self, repositorio):
        self.repo = repositorio

    def evaluar_logros_tras_test(
        self,
        resultado_test: Dict[str, Any],
        nivel_actual: int,
        racha_dias: int,
    ) -> List[Dict[str, Any]]:
        """
        Revisa las condiciones de todos los logros tras completar un test.
        Retorna la lista de nuevos logros desbloqueados en esta sesión.
        """
        nuevos_desbloqueados: List[Dict[str, Any]] = []

        aprobado = resultado_test.get("aprobado", False)
        puntaje = resultado_test.get("puntaje_porcentaje", 0.0)

        # 1. Primer paso
        if aprobado:
            logro = self.repo.desbloquear_logro("primer_paso")
            if logro:
                nuevos_desbloqueados.append(logro)

        # 2. Puntaje perfecto (100%)
        if puntaje >= 100.0:
            logro = self.repo.desbloquear_logro("puntaje_perfecto")
            if logro:
                nuevos_desbloqueados.append(logro)

        # 3. Racha imparable (>= 5 días)
        if racha_dias >= 5:
            logro = self.repo.desbloquear_logro("racha_imparable")
            if logro:
                nuevos_desbloqueados.append(logro)

        # 4. Reina del ICFES (Nivel 3+)
        if nivel_actual >= 3:
            logro = self.repo.desbloquear_logro("reina_del_icfes")
            if logro:
                nuevos_desbloqueados.append(logro)

        # 5. Consultar estadísticas acumuladas para logros de volumen
        stats = self.repo.obtener_estadisticas_generales()

        # Ojo de Halcón (10 aciertos literales acumulados)
        with self.repo.obtener_sesion() as s:
            from sqlalchemy import func
            from ..datos.modelos import TestResultado, SesionLectura

            total_lit = s.query(func.sum(TestResultado.aciertos_literal)).scalar() or 0
            if total_lit >= 10:
                logro = self.repo.desbloquear_logro("ojo_de_halcon")
                if logro:
                    nuevos_desbloqueados.append(logro)

            # Cerebro Crítico (5 aciertos críticos acumulados)
            total_crit = s.query(func.sum(TestResultado.aciertos_critico)).scalar() or 0
            if total_crit >= 5:
                logro = self.repo.desbloquear_logro("cerebro_critico")
                if logro:
                    nuevos_desbloqueados.append(logro)

            # Guardiana de Mitos (3 leyendas o mitos leídos)
            mitos_leidos = s.query(SesionLectura).filter(
                SesionLectura.subtipo.in_(["mito_indigena", "leyenda", "leyenda_muisca", "leyenda_colombiana"])
            ).count()
            if mitos_leidos >= 3:
                logro = self.repo.desbloquear_logro("lectora_de_mitos")
                if logro:
                    nuevos_desbloqueados.append(logro)

            # Curiosidad Científica (3 textos de ciencias)
            ciencias_leidas = s.query(SesionLectura).filter(
                SesionLectura.subtipo.in_(["ciencias_naturales", "astronomia", "ciencias_ambientales", "oceanografia", "neurociencia"])
            ).count()
            if ciencias_leidas >= 3:
                logro = self.repo.desbloquear_logro("amiga_de_la_ciencia")
                if logro:
                    nuevos_desbloqueados.append(logro)

        return nuevos_desbloqueados

    def actualizar_mascota(self, aprobado: bool, puntaje: float) -> Dict[str, Any]:
        """Otorga experiencia y frases de ánimo a Koko el Colibrí."""
        xp_base = 35 if aprobado else 15
        if puntaje >= 100.0:
            xp_base += 25

        frases_victoria = [
            "¡Qué vuelo tan alto dimos hoy! Eres genial.",
            "¡Leíste con la precisión de un halcón!",
            "¡Mi corazón late a mil por hora de la emoción!",
            "¡Cada día eres más sabia y perspicaz!",
        ]
        frases_animo = [
            "No pasa nada, cada intento entrena nuestras alas.",
            "Respira hondo; la próxima lectura será nuestra.",
            "¡Estoy contigo en cada página, vamos a lograrlo!",
        ]

        frase = random.choice(frases_victoria) if aprobado else random.choice(frases_animo)
        return self.repo.sumar_experiencia_mascota(xp_base, frase)

    @staticmethod
    def girar_ruleta_bonificacion() -> Dict[str, Any]:
        """
        Ruleta de la suerte que se activa exclusivamente ante puntaje perfecto (100%).
        Premios de mérito educativo y recreativo.
        """
        opciones = [
            {"tipo": "tiempo", "valor": 15, "nombre": "+15 Minutos Extra de Juego 🎮", "icono": "⏱️"},
            {"tipo": "tiempo", "valor": 20, "nombre": "+20 Minutos Extra de Juego 🚀", "icono": "🎉"},
            {"tipo": "xp", "valor": 60, "nombre": "+60 XP para Koko el Colibrí 🦉", "icono": "⭐"},
            {"tipo": "doble", "valor": 30, "nombre": "¡Súper Recompensa de +30 Minutos! 👑", "icono": "💎"},
        ]
        return random.choice(opciones)

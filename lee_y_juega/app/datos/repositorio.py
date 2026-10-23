"""
Capa de repositorio para Lee y Juega.
Maneja operaciones de base de datos SQLite con SQLAlchemy.
"""
from __future__ import annotations

import csv
import json
import logging
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import Session, sessionmaker

from .modelos import (
    Base,
    HistorialNivel,
    LeccionProgreso,
    RegistroTiempo,
    SesionLectura,
    TestResultado,
)
from ..config.configuracion import obtener_ruta_datos

logger = logging.getLogger(__name__)


class RepositorioDatos:
    """Acceso centralizado a los datos locales."""

    def __init__(self, ruta_db: Optional[Path] = None):
        self.ruta_db = ruta_db or (obtener_ruta_datos() / "lee_y_juega.db")
        self.engine = create_engine(
            f"sqlite:///{self.ruta_db.as_posix()}",
            connect_args={"check_same_thread": False},
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.inicializar_base_de_datos()

    def inicializar_base_de_datos(self) -> None:
        """Crea las tablas si no existen e inicializa registros requeridos."""
        self.ruta_db.parent.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"Base de datos verificada en {self.ruta_db}")

        # Inicializar lecciones si están vacías
        with self.obtener_sesion() as s:
            for tipo in ["literal", "inferencial", "critico"]:
                existente = s.query(LeccionProgreso).filter_by(tipo_lectura=tipo).first()
                if not existente:
                    s.add(LeccionProgreso(tipo_lectura=tipo, completada=False))
            s.commit()

    def obtener_sesion(self) -> Session:
        return self.SessionLocal()

    # --- BANCO DE TIEMPO ---

    def obtener_o_crear_registro_hoy(self, s: Session) -> RegistroTiempo:
        hoy = date.today()
        reg = s.query(RegistroTiempo).filter_by(fecha=hoy).first()
        if not reg:
            reg = RegistroTiempo(
                fecha=hoy,
                minutos_ganados=0.0,
                minutos_gastados=0.0,
                minutos_ajustados=0.0,
                balance_disponible=0.0,
            )
            s.add(reg)
            s.flush()
        return reg

    def obtener_balance_actual(self) -> float:
        with self.obtener_sesion() as s:
            reg = self.obtener_o_crear_registro_hoy(s)
            return float(reg.balance_disponible)

    def sumar_minutos(self, minutos: float) -> float:
        """Agrega minutos ganados por aprobar lecturas."""
        with self.obtener_sesion() as s:
            reg = self.obtener_o_crear_registro_hoy(s)
            reg.minutos_ganados += minutos
            reg.balance_disponible += minutos
            nuevo_balance = reg.balance_disponible
            s.commit()
            logger.info(f"Se sumaron {minutos} min. Nuevo balance: {nuevo_balance}")
            return float(nuevo_balance)

    def descontar_minutos(self, minutos: float) -> float:
        """Descuenta minutos mientras la actividad es ocio."""
        with self.obtener_sesion() as s:
            reg = self.obtener_o_crear_registro_hoy(s)
            reg.minutos_gastados += minutos
            reg.balance_disponible = max(0.0, reg.balance_disponible - minutos)
            nuevo_balance = reg.balance_disponible
            s.commit()
            return float(nuevo_balance)

    def ajustar_minutos_manual(self, delta_minutos: float) -> float:
        """Permite al padre añadir o retirar tiempo."""
        with self.obtener_sesion() as s:
            reg = self.obtener_o_crear_registro_hoy(s)
            reg.minutos_ajustados += delta_minutos
            reg.balance_disponible = max(0.0, reg.balance_disponible + delta_minutos)
            nuevo_balance = reg.balance_disponible
            s.commit()
            return float(nuevo_balance)

    # --- NIVELES ADAPTATIVOS ---

    def obtener_nivel_actual(self) -> int:
        with self.obtener_sesion() as s:
            ultimo = s.query(HistorialNivel).order_by(desc(HistorialNivel.id)).first()
            if ultimo:
                return int(ultimo.nivel_nuevo)
            return 1

    def registrar_cambio_nivel(self, nuevo_nivel: int, razon: str) -> None:
        nivel_actual = self.obtener_nivel_actual()
        if nuevo_nivel == nivel_actual:
            return
        with self.obtener_sesion() as s:
            nuevo = HistorialNivel(
                nivel_anterior=nivel_actual,
                nivel_nuevo=nuevo_nivel,
                razon=razon,
            )
            s.add(nuevo)
            s.commit()
            logger.info(f"Nivel actualizado: {nivel_actual} -> {nuevo_nivel} ({razon})")

    # --- LECTURAS Y TESTS ---

    def guardar_sesion_lectura(
        self,
        titulo: str,
        tipo_texto: str,
        subtipo: Optional[str],
        nivel: int,
        fuente: str,
        palabras: int,
        duracion_segundos: int,
    ) -> int:
        with self.obtener_sesion() as s:
            sesion = SesionLectura(
                titulo=titulo,
                tipo_texto=tipo_texto,
                subtipo=subtipo,
                nivel=nivel,
                fuente=fuente,
                palabras=palabras,
                duracion_segundos=duracion_segundos,
            )
            s.add(sesion)
            s.commit()
            return int(sesion.id)

    def guardar_test_resultado(
        self,
        sesion_id: Optional[int],
        nivel: int,
        total_preguntas: int,
        aciertos: int,
        puntaje_porcentaje: float,
        aprobado: bool,
        aciertos_literal: int,
        total_literal: int,
        aciertos_inferencial: int,
        total_inferencial: int,
        aciertos_critico: int,
        total_critico: int,
        detalle: Optional[Dict[str, Any]] = None,
    ) -> int:
        with self.obtener_sesion() as s:
            resultado = TestResultado(
                sesion_id=sesion_id,
                nivel=nivel,
                total_preguntas=total_preguntas,
                aciertos=aciertos,
                puntaje_porcentaje=puntaje_porcentaje,
                aprobado=aprobado,
                aciertos_literal=aciertos_literal,
                total_literal=total_literal,
                aciertos_inferencial=aciertos_inferencial,
                total_inferencial=total_inferencial,
                aciertos_critico=aciertos_critico,
                total_critico=total_critico,
                detalle_json=json.dumps(detalle, ensure_ascii=False) if detalle else None,
            )
            s.add(resultado)
            s.commit()
            return int(resultado.id)

    def obtener_ultimos_tests(self, limite: int = 10) -> List[TestResultado]:
        with self.obtener_sesion() as s:
            return s.query(TestResultado).order_by(desc(TestResultado.fecha)).limit(limite).all()

    # --- LECCIONES INTERACTIVAS ---

    def ha_completado_leccion(self, tipo_lectura: str) -> bool:
        with self.obtener_sesion() as s:
            leccion = s.query(LeccionProgreso).filter_by(tipo_lectura=tipo_lectura).first()
            return bool(leccion and leccion.completada)

    def marcar_leccion_completada(self, tipo_lectura: str) -> None:
        with self.obtener_sesion() as s:
            leccion = s.query(LeccionProgreso).filter_by(tipo_lectura=tipo_lectura).first()
            if leccion:
                leccion.completada = True
                leccion.fecha_completada = datetime.now()
            else:
                s.add(LeccionProgreso(tipo_lectura=tipo_lectura, completada=True, fecha_completada=datetime.now()))
            s.commit()

    # --- RACHA Y ESTADÍSTICAS ---

    def calcular_racha_dias(self) -> int:
        """Calcula cuántos días seguidos lleva aprobando al menos un test."""
        with self.obtener_sesion() as s:
            # Fechas únicas con tests aprobados
            fechas_query = (
                s.query(func.date(TestResultado.fecha))
                .filter(TestResultado.aprobado == True)
                .group_by(func.date(TestResultado.fecha))
                .order_by(desc(func.date(TestResultado.fecha)))
                .all()
            )
            fechas = [datetime.strptime(f[0], "%Y-%m-%d").date() for f in fechas_query]
            if not fechas:
                return 0

            hoy = date.today()
            ayer = hoy - timedelta(days=1)
            
            # La racha puede incluir hoy o ayer
            if fechas[0] != hoy and fechas[0] != ayer:
                return 0

            racha = 1
            cursor = fechas[0]
            for f in fechas[1:]:
                if f == cursor - timedelta(days=1):
                    racha += 1
                    cursor = f
                else:
                    break
            return racha

    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """Obtiene resumen completo de métricas pedagógicas y de tiempo."""
        with self.obtener_sesion() as s:
            total_tests = s.query(TestResultado).count()
            aprobados = s.query(TestResultado).filter(TestResultado.aprobado == True).count()
            reprobados = total_tests - aprobados

            tasa_aprobacion = (aprobados / total_tests * 100) if total_tests > 0 else 0.0

            # Totales y aciertos por dimensión
            lit_aciertos = s.query(func.sum(TestResultado.aciertos_literal)).scalar() or 0
            lit_total = s.query(func.sum(TestResultado.total_literal)).scalar() or 0
            inf_aciertos = s.query(func.sum(TestResultado.aciertos_inferencial)).scalar() or 0
            inf_total = s.query(func.sum(TestResultado.total_inferencial)).scalar() or 0
            crit_aciertos = s.query(func.sum(TestResultado.aciertos_critico)).scalar() or 0
            crit_total = s.query(func.sum(TestResultado.total_critico)).scalar() or 0

            pct_literal = (lit_aciertos / lit_total * 100) if lit_total > 0 else 0.0
            pct_inferencial = (inf_aciertos / inf_total * 100) if inf_total > 0 else 0.0
            pct_critico = (crit_aciertos / crit_total * 100) if crit_total > 0 else 0.0

            minutos_leidos = s.query(func.sum(SesionLectura.duracion_segundos)).scalar() or 0
            minutos_leidos = round(minutos_leidos / 60, 1)

            minutos_jugados = s.query(func.sum(RegistroTiempo.minutos_gastados)).scalar() or 0.0

            return {
                "total_tests": total_tests,
                "aprobados": aprobados,
                "reprobados": reprobados,
                "tasa_aprobacion": round(tasa_aprobacion, 1),
                "nivel_actual": self.obtener_nivel_actual(),
                "racha_dias": self.calcular_racha_dias(),
                "pct_literal": round(pct_literal, 1),
                "pct_inferencial": round(pct_inferencial, 1),
                "pct_critico": round(pct_critico, 1),
                "minutos_leidos": minutos_leidos,
                "minutos_jugados": round(minutos_jugados, 1),
            }

    def obtener_historial_tiempos_ultimos_dias(self, dias: int = 7) -> List[Dict[str, Any]]:
        """Retorna el historial diario de minutos leídos y jugados."""
        fecha_desde = date.today() - timedelta(days=dias - 1)
        with self.obtener_sesion() as s:
            registros = (
                s.query(RegistroTiempo)
                .filter(RegistroTiempo.fecha >= fecha_desde)
                .order_by(RegistroTiempo.fecha)
                .all()
            )
            resultado = []
            for r in registros:
                resultado.append({
                    "fecha": r.fecha.strftime("%d/%m"),
                    "ganados": r.minutos_ganados,
                    "gastados": r.minutos_gastados,
                })
            return resultado

    # --- EXPORTACIÓN Y COPIA DE SEGURIDAD ---

    def exportar_csv(self, ruta_destino: Path) -> bool:
        """Exporta los tests y sesiones a formato CSV."""
        try:
            with self.obtener_sesion() as s:
                tests = s.query(TestResultado).order_by(TestResultado.fecha).all()
                with open(ruta_destino, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "ID", "Fecha", "Nivel", "Total Preguntas", "Aciertos",
                        "Puntaje (%)", "Aprobado",
                        "Literal (Aciertos/Total)", "Inferencial (Aciertos/Total)", "Crítico (Aciertos/Total)"
                    ])
                    for t in tests:
                        writer.writerow([
                            t.id,
                            t.fecha.strftime("%Y-%m-%d %H:%M"),
                            t.nivel,
                            t.total_preguntas,
                            t.aciertos,
                            f"{t.puntaje_porcentaje:.1f}",
                            "Sí" if t.aprobado else "No",
                            f"{t.aciertos_literal}/{t.total_literal}",
                            f"{t.aciertos_inferencial}/{t.total_inferencial}",
                            f"{t.aciertos_critico}/{t.total_critico}",
                        ])
            return True
        except Exception as e:
            logger.error(f"Error al exportar CSV: {e}")
            return False

    def respaldar_base_datos(self, ruta_destino: Path) -> bool:
        """Copia de seguridad del archivo SQLite."""
        try:
            ruta_destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.ruta_db, ruta_destino)
            return True
        except Exception as e:
            logger.error(f"Error al respaldar base de datos: {e}")
            return False

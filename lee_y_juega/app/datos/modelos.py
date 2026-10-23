"""
Modelos de datos con SQLAlchemy para Lee y Juega.
Almacena progreso, lecturas, resultados de pruebas, tiempos y niveles.
"""
from __future__ import annotations

from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class SesionLectura(Base):
    """Registra cada lectura iniciada o completada."""
    __tablename__ = "sesiones_lectura"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, default=datetime.now, nullable=False)
    titulo = Column(String(255), nullable=False)
    tipo_texto = Column(String(64), nullable=False)  # literario, informativo, discontinuo
    subtipo = Column(String(64), nullable=True)     # fábula, cuento, noticia, gráfica, tabla
    nivel = Column(Integer, default=1, nullable=False)
    fuente = Column(String(64), default="banco_offline", nullable=False)
    palabras = Column(Integer, default=0, nullable=False)
    duracion_segundos = Column(Integer, default=0, nullable=False)

    tests = relationship("TestResultado", back_populates="sesion", cascade="all, delete-orphan")


class TestResultado(Base):
    """Guarda el resultado detallado de cada evaluación."""
    __tablename__ = "tests_resultado"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sesion_id = Column(Integer, ForeignKey("sesiones_lectura.id"), nullable=True)
    fecha = Column(DateTime, default=datetime.now, nullable=False)
    nivel = Column(Integer, default=1, nullable=False)
    total_preguntas = Column(Integer, default=0, nullable=False)
    aciertos = Column(Integer, default=0, nullable=False)
    puntaje_porcentaje = Column(Float, default=0.0, nullable=False)
    aprobado = Column(Boolean, default=False, nullable=False)

    # Desglose por dimensiones del ICFES
    aciertos_literal = Column(Integer, default=0, nullable=False)
    total_literal = Column(Integer, default=0, nullable=False)
    aciertos_inferencial = Column(Integer, default=0, nullable=False)
    total_inferencial = Column(Integer, default=0, nullable=False)
    aciertos_critico = Column(Integer, default=0, nullable=False)
    total_critico = Column(Integer, default=0, nullable=False)

    # JSON con preguntas, respuestas del usuario y explicaciones
    detalle_json = Column(Text, nullable=True)

    sesion = relationship("SesionLectura", back_populates="tests")


class RegistroTiempo(Base):
    """Bitácora diaria de minutos ganados, consumidos y ajustados."""
    __tablename__ = "registro_tiempo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(Date, default=date.today, unique=True, nullable=False)
    minutos_ganados = Column(Float, default=0.0, nullable=False)
    minutos_gastados = Column(Float, default=0.0, nullable=False)
    minutos_ajustados = Column(Float, default=0.0, nullable=False)  # Por el padre
    balance_disponible = Column(Float, default=0.0, nullable=False)
    ultima_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class HistorialNivel(Base):
    """Historial de cambios de dificultad adaptativa."""
    __tablename__ = "historial_nivel"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, default=datetime.now, nullable=False)
    nivel_anterior = Column(Integer, nullable=False)
    nivel_nuevo = Column(Integer, nullable=False)
    razon = Column(String(255), nullable=False)


class LeccionProgreso(Base):
    """Estado de completitud de lecciones interactivas para enseñar primero."""
    __tablename__ = "lecciones_progreso"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_lectura = Column(String(32), unique=True, nullable=False)  # literal, inferencial, critico
    completada = Column(Boolean, default=False, nullable=False)
    fecha_completada = Column(DateTime, nullable=True)


class Logro(Base):
    """Sistema de medallas, insignias y logros para motivar el mérito."""
    __tablename__ = "logros"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(64), unique=True, nullable=False)
    nombre = Column(String(128), nullable=False)
    descripcion = Column(String(255), nullable=False)
    icono = Column(String(16), default="🏅", nullable=False)
    desbloqueado = Column(Boolean, default=False, nullable=False)
    fecha_desbloqueo = Column(DateTime, nullable=True)


class MascotaEstado(Base):
    """Estado y evolución del compañero virtual de lectura (Koko el Colibrí)."""
    __tablename__ = "mascota_estado"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(64), default="Koko el Colibrí", nullable=False)
    nivel = Column(Integer, default=1, nullable=False)
    experiencia = Column(Integer, default=0, nullable=False)
    accesorio = Column(String(64), default="bufanda_azul", nullable=False)
    frase_actual = Column(String(255), default="¡Hola! Estoy listo para leer contigo.", nullable=False)


class SimulacroResultado(Base):
    """Resultados de mini-simulacros formales tipo prueba Saber 7.°."""
    __tablename__ = "simulacros_resultado"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, default=datetime.now, nullable=False)
    puntaje_global = Column(Float, default=0.0, nullable=False)  # Escala 0-100
    nivel_desempeno = Column(String(32), default="Básico", nullable=False)  # Insuficiente, Mínimo, Satisfactorio, Avanzado
    total_preguntas = Column(Integer, default=15, nullable=False)
    aciertos = Column(Integer, default=0, nullable=False)
    tiempo_empleado_segundos = Column(Integer, default=0, nullable=False)
    diagnostico_texto = Column(Text, nullable=True)


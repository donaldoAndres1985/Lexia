"""
Pruebas de base de datos SQLite y capa de repositorio.
"""
from datetime import date
from pathlib import Path
import tempfile
from lee_y_juega.app.datos.repositorio import RepositorioDatos


def test_repositorio_banco_tiempo():
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_db = Path(tmpdir) / "test.db"
        repo = RepositorioDatos(ruta_db)

        # Balance inicial debe ser 0
        assert repo.obtener_balance_actual() == 0.0

        # Sumar 60 minutos
        nuevo_bal = repo.sumar_minutos(60.0)
        assert nuevo_bal == 60.0
        assert repo.obtener_balance_actual() == 60.0

        # Descontar 15 minutos
        descontado = repo.descontar_minutos(15.0)
        assert descontado == 45.0
        assert repo.obtener_balance_actual() == 45.0
        repo.cerrar()


def test_repositorio_niveles():
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_db = Path(tmpdir) / "test.db"
        repo = RepositorioDatos(ruta_db)

        # Nivel por defecto
        assert repo.obtener_nivel_actual() == 1

        repo.registrar_cambio_nivel(2, "Test aprobados con honores")
        assert repo.obtener_nivel_actual() == 2
        repo.cerrar()


def test_repositorio_lecciones_progreso():
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_db = Path(tmpdir) / "test.db"
        repo = RepositorioDatos(ruta_db)

        assert repo.ha_completado_leccion("literal") is False
        repo.marcar_leccion_completada("literal")
        assert repo.ha_completado_leccion("literal") is True
        repo.cerrar()

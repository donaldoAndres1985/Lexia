"""
Pruebas del banco de tiempo y control de horarios.
"""
from pathlib import Path
import tempfile
from lee_y_juega.app.datos.repositorio import RepositorioDatos
from lee_y_juega.app.nucleo.banco_tiempo import BancoTiempo


class MockConfigBanco:
    def obtener(self, clave, default=None):
        if clave == "tiempo_recompensa_min":
            return 60.0
        if clave == "tiempo_ocio_inicial_min":
            return 30.0
        if clave == "horario_ocio_inicio":
            return "00:00"
        if clave == "horario_ocio_fin":
            return "23:59"
        return default


def test_recompensa_lectura():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = RepositorioDatos(Path(tmpdir) / "test_banco.db")
        config = MockConfigBanco()
        banco = BancoTiempo(repo, config)

        # Inicia con ocio inicial de 30 min configurado
        assert banco.minutos_disponibles == 30.0

        # Al aprobar lectura, suma los 60 min de recompensa
        nuevo_saldo = banco.agregar_recompensa_lectura()
        assert nuevo_saldo == 90.0
        assert banco.minutos_disponibles == 90.0


def test_ajuste_manual():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = RepositorioDatos(Path(tmpdir) / "test_banco2.db")
        config = MockConfigBanco()
        banco = BancoTiempo(repo, config)

        banco.ajustar_manualmente(20.0)
        assert banco.minutos_disponibles == 50.0

        banco.ajustar_manualmente(-10.0)
        assert banco.minutos_disponibles == 40.0

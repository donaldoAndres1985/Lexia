"""
Pruebas del gestor de dificultad adaptativa.
"""
from pathlib import Path
import tempfile
from lee_y_juega.app.datos.repositorio import RepositorioDatos
from lee_y_juega.app.lectura.dificultad import GestorDificultadAdaptativa


class MockConfigDificultad:
    def obtener(self, clave, default=None):
        if clave == "subir_nivel_consecutivos":
            return 3
        if clave == "subir_nivel_min_puntaje":
            return 85.0
        if clave == "bajar_nivel_consecutivos":
            return 2
        return default


def test_subir_nivel_tras_3_exitos():
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_db = Path(tmpdir) / "test_dif.db"
        repo = RepositorioDatos(ruta_db)
        config = MockConfigDificultad()
        gestor = GestorDificultadAdaptativa(repo, config)

        assert repo.obtener_nivel_actual() == 1

        # Registrar 3 tests aprobados con >= 85%
        for _ in range(3):
            repo.guardar_test_resultado(
                sesion_id=None,
                nivel=1,
                total_preguntas=5,
                aciertos=5,
                puntaje_porcentaje=100.0,
                aprobado=True,
                aciertos_literal=2,
                total_literal=2,
                aciertos_inferencial=2,
                total_inferencial=2,
                aciertos_critico=1,
                total_critico=1,
            )

        nuevo_nivel, msg = gestor.verificar_y_actualizar_nivel()
        assert nuevo_nivel == 2
        assert "subiste al Nivel 2" in msg
        assert repo.obtener_nivel_actual() == 2

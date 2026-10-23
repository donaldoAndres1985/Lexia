"""
Pruebas del sistema de gamificación positiva, logros y evolución de Koko.
"""
from pathlib import Path
import tempfile
from lee_y_juega.app.datos.repositorio import RepositorioDatos
from lee_y_juega.app.pedagogia.gamificacion import GestorGamificacion


def test_desbloqueo_primer_paso_y_perfecto():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = RepositorioDatos(Path(tmpdir) / "test_gam.db")
        gestor = GestorGamificacion(repo)

        resultado_100 = {
            "aprobado": True,
            "puntaje_porcentaje": 100.0,
            "desglose": {
                "literal": {"aciertos": 2, "total": 2},
                "inferencial": {"aciertos": 2, "total": 2},
                "critico": {"aciertos": 1, "total": 1},
            }
        }

        nuevos = gestor.evaluar_logros_tras_test(resultado_100, nivel_actual=1, racha_dias=1)
        codigos = [l["codigo"] for l in nuevos]

        assert "primer_paso" in codigos
        assert "puntaje_perfecto" in codigos
        repo.cerrar()


def test_evolucion_mascota():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = RepositorioDatos(Path(tmpdir) / "test_pet.db")
        gestor = GestorGamificacion(repo)

        estado_inicial = repo.obtener_estado_mascota()
        assert estado_inicial["nivel"] == 1
        assert estado_inicial["experiencia"] == 0

        # Sumar experiencia
        nuevo = gestor.actualizar_mascota(aprobado=True, puntaje=100.0)
        assert nuevo["experiencia"] > 0
        assert nuevo["frase"] != ""
        repo.cerrar()


def test_ruleta_bonificacion():
    premio = GestorGamificacion.girar_ruleta_bonificacion()
    assert "tipo" in premio
    assert "valor" in premio
    assert "nombre" in premio
    assert premio["valor"] > 0

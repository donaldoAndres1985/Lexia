"""
Pruebas del mini-simulacro oficial ICFES Saber 7.° y del generador de cuadernillos imprimibles.
"""
from pathlib import Path
import tempfile
from lee_y_juega.app.datos.repositorio import RepositorioDatos
from lee_y_juega.app.lectura.fuentes import GestorFuentesLectura
from lee_y_juega.app.lectura.simulacro import GestorSimulacro
from lee_y_juega.app.lectura.generador_imprimible import GeneradorImprimibleICFES


def test_generar_y_calificar_simulacro():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = RepositorioDatos(Path(tmpdir) / "test_sim.db")
        fuentes = GestorFuentesLectura()
        gestor = GestorSimulacro(fuentes, repo)

        sim = gestor.generar_simulacro_15_preguntas()
        assert len(sim["preguntas"]) == 15
        assert len(sim["bloques"]) == 3

        # Calificar todas correctas (100 puntos -> Avanzado)
        respuestas = [p.get("correcta", 0) for p in sim["preguntas"]]
        resultado = gestor.calificar_simulacro(sim["preguntas"], respuestas, tiempo_empleado_segundos=600)

        assert resultado["puntaje_global"] == 100.0
        assert resultado["nivel_desempeno"] == "Avanzado"
        assert resultado["aciertos"] == 15
        repo.cerrar()


def test_generador_cuadernillo_html_imprimible():
    with tempfile.TemporaryDirectory() as tmpdir:
        fuentes = GestorFuentesLectura()
        lectura = fuentes.lecturas_offline[0]
        preguntas = lectura.get("preguntas", [])

        ruta_html = Path(tmpdir) / "cuadernillo_prueba.html"
        salida = GeneradorImprimibleICFES.generar_cuadernillo_html(lectura, preguntas, ruta_html)

        assert salida.exists()
        contenido = salida.read_text(encoding="utf-8")
        assert "Saber 7.°" in contenido
        assert "SECCIÓN DE BURBUJAS DE RESPUESTA" in contenido
        assert "Clave de Respuestas" in contenido

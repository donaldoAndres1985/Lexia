"""
Pruebas del evaluador de pruebas de Lectura Crítica.
"""
from lee_y_juega.app.lectura.calificacion import EvaluadorTest


def test_evaluacion_aprobada():
    evaluador = EvaluadorTest(umbral_aprobacion=70.0)
    preguntas = [
        {"enunciado": "P1", "opciones": ["A", "B", "C", "D"], "correcta": 0, "nivel": "literal", "explicacion": "E1"},
        {"enunciado": "P2", "opciones": ["A", "B", "C", "D"], "correcta": 1, "nivel": "inferencial", "explicacion": "E2"},
        {"enunciado": "P3", "opciones": ["A", "B", "C", "D"], "correcta": 2, "nivel": "critico", "explicacion": "E3"},
        {"enunciado": "P4", "opciones": ["A", "B", "C", "D"], "correcta": 3, "nivel": "literal", "explicacion": "E4"},
    ]
    respuestas_usuario = [0, 1, 2, 0]  # 3 aciertos de 4 = 75% -> Aprobado
    resultado = evaluador.evaluar(preguntas, respuestas_usuario)

    assert resultado["total_preguntas"] == 4
    assert resultado["aciertos"] == 3
    assert resultado["puntaje_porcentaje"] == 75.0
    assert resultado["aprobado"] is True
    assert resultado["desglose"]["literal"]["aciertos"] == 1
    assert resultado["desglose"]["literal"]["total"] == 2
    assert resultado["desglose"]["inferencial"]["aciertos"] == 1
    assert resultado["desglose"]["critico"]["aciertos"] == 1


def test_evaluacion_reprobada():
    evaluador = EvaluadorTest(umbral_aprobacion=70.0)
    preguntas = [
        {"enunciado": "P1", "opciones": ["A", "B", "C", "D"], "correcta": 0, "nivel": "literal", "explicacion": "E1"},
        {"enunciado": "P2", "opciones": ["A", "B", "C", "D"], "correcta": 1, "nivel": "inferencial", "explicacion": "E2"},
    ]
    respuestas_usuario = [1, 0]  # 0 aciertos de 2 = 0% -> Reprobado
    resultado = evaluador.evaluar(preguntas, respuestas_usuario)

    assert resultado["aciertos"] == 0
    assert resultado["puntaje_porcentaje"] == 0.0
    assert resultado["aprobado"] is False

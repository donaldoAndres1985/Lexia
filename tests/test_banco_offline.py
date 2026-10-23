"""
Pruebas del banco offline de lecturas.
Verifica que contenga al menos 40 lecturas con sus preguntas correspondientes.
"""
from lee_y_juega.app.lectura.banco_catalogo import construir_catalogo_40_lecturas


def test_catalogo_minimo_40_lecturas():
    lecturas = construir_catalogo_40_lecturas()
    assert len(lecturas) >= 40, f"Se esperaban al menos 40 lecturas, pero hay {len(lecturas)}"


def test_estructura_lecturas_y_preguntas():
    lecturas = construir_catalogo_40_lecturas()
    for l in lecturas:
        assert "id" in l and l["id"]
        assert "titulo" in l and l["titulo"]
        assert "tipo_texto" in l and l["tipo_texto"] in ["literario", "informativo", "discontinuo"]
        assert "nivel" in l and 1 <= l["nivel"] <= 6
        assert "texto" in l and len(l["texto"]) > 50

        # Verificar preguntas
        preguntas = l.get("preguntas", [])
        assert len(preguntas) >= 3, f"La lectura {l['id']} debe tener al menos 3 preguntas"
        for p in preguntas:
            assert "enunciado" in p and p["enunciado"]
            assert "opciones" in p and len(p["opciones"]) == 4
            assert 0 <= p["correcta"] <= 3
            assert p["nivel"] in ["literal", "inferencial", "critico"]
            assert "explicacion" in p and p["explicacion"]

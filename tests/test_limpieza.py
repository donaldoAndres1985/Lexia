"""
Pruebas del filtro de adecuación, longitud y limpieza de texto.
"""
from lee_y_juega.app.lectura.limpieza import FiltroAdecuacionYLimpieza


def test_limpieza_html_y_wiki():
    texto_sucio = "<p>Texto con <b>etiquetas</b> y [1] referencias [editar].</p>"
    limpio = FiltroAdecuacionYLimpieza.limpiar_texto(texto_sucio)
    assert "<p>" not in limpio
    assert "<b>" not in limpio
    assert "[1]" not in limpio
    assert "[editar]" not in limpio
    assert "Texto con etiquetas y referencias." in limpio


def test_filtro_palabras_prohibidas():
    texto_seguro = "Las mariposas vuelan en el jardín botánico de Medellín."
    aprobado, razon = FiltroAdecuacionYLimpieza.es_apropiado_heuristico(texto_seguro)
    assert aprobado is True

    texto_peligroso = "El cargamento de cocaína fue interceptado."
    aprobado2, razon2 = FiltroAdecuacionYLimpieza.es_apropiado_heuristico(texto_peligroso)
    assert aprobado2 is False
    assert "cocaína" in razon2.lower()


def test_conteo_palabras():
    frase = "El río Magdalena baña las tierras de Colombia."
    assert FiltroAdecuacionYLimpieza.contar_palabras(frase) == 8

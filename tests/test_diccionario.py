"""
Pruebas del glosario y diccionario contextual ICFES para 7.º grado.
"""
from lee_y_juega.app.lectura.diccionario import GlosarioContextual


def test_busqueda_palabras_clave_icfes():
    # Búsqueda exacta
    res1 = GlosarioContextual.buscar("efímero")
    assert res1 is not None
    assert "fugaz" in res1["definicion"].lower()
    assert "sinonimos" in res1

    res2 = GlosarioContextual.buscar("verosímil")
    assert res2 is not None
    assert "creíble" in res2["definicion"].lower()

    res3 = GlosarioContextual.buscar("refutar")
    assert res3 is not None
    assert "falso" in res3["definicion"].lower()


def test_limpieza_puntuacion_diccionario():
    # Con comas o signos adyacentes
    res = GlosarioContextual.buscar("«sesgo,»")
    assert res is not None
    assert "prejuicio" in res["sinonimos"].lower()

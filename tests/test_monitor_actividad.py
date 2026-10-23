"""
Pruebas del clasificador de actividad (Ocio / Estudio / Neutro).
"""
from lee_y_juega.app.config.configuracion import ConfiguracionSistema
from lee_y_juega.app.nucleo.monitor_actividad import CategoriaActividad, MonitorActividad


class MockConfig:
    def obtener(self, clave, default=None):
        if clave == "apps_ocio":
            return ["RobloxPlayerBeta.exe", "javaw.exe"]
        if clave == "titulos_ocio":
            return ["YouTube", "TikTok", "Twitch"]
        if clave == "apps_estudio":
            return ["WINWORD.EXE"]
        if clave == "titulos_estudio":
            return ["Classroom", "Wikipedia", "Khan Academy"]
        if clave == "titulos_musica_permitida":
            return ["Spotify"]
        return default


def test_clasificacion_ocio_por_proceso():
    monitor = MonitorActividad(MockConfig())
    cat = monitor.clasificar("RobloxPlayerBeta.exe", "Roblox Game")
    assert cat == CategoriaActividad.OCIO


def test_clasificacion_ocio_por_titulo():
    monitor = MonitorActividad(MockConfig())
    cat = monitor.clasificar("chrome.exe", "Videos divertidos - YouTube")
    assert cat == CategoriaActividad.OCIO


def test_clasificacion_estudio():
    monitor = MonitorActividad(MockConfig())
    cat = monitor.clasificar("chrome.exe", "Tarea de Biología - Google Classroom")
    assert cat == CategoriaActividad.ESTUDIO

    cat2 = monitor.clasificar("WINWORD.EXE", "Documento1 - Word")
    assert cat2 == CategoriaActividad.ESTUDIO


def test_clasificacion_neutro():
    monitor = MonitorActividad(MockConfig())
    cat = monitor.clasificar("explorer.exe", "Explorador de archivos")
    assert cat == CategoriaActividad.NEUTRO

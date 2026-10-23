"""
Hojas de estilo QSS y paleta de diseño para Lee y Juega.
Diseño moderno, cálido, limpio y amigable para una niña de 12 años.
"""
from __future__ import annotations

# Paleta de colores
COLOR_PRIMARIO = "#4F46E5"        # Índigo moderno
COLOR_PRIMARIO_HOVER = "#4338CA"
COLOR_SECUNDARIO = "#06B6D4"      # Cian brillante
COLOR_EXITO = "#10B981"           # Esmeralda positivo
COLOR_ADVERTENCIA = "#F59E0B"     # Ámbar suave
COLOR_FONDO = "#F8FAFC"           # Blanco grisáceo muy suave
COLOR_SUPERFICIE = "#FFFFFF"      # Blanco puro tarjetas
COLOR_TEXTO_TITULO = "#1E293B"    # Pizarra oscuro
COLOR_TEXTO_CUERPO = "#334155"    # Pizarra medio
COLOR_BORDE = "#E2E8F0"           # Gris claro sutil


def obtener_estilo_general(tamano_fuente: str = "normal") -> str:
    """Retorna la hoja de estilos global en formato QSS."""
    base_font_size = "15px" if tamano_fuente == "normal" else "17px"
    h1_size = "24px" if tamano_fuente == "normal" else "28px"
    h2_size = "20px" if tamano_fuente == "normal" else "23px"

    return f"""
    QWidget {{
        font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
        font-size: {base_font_size};
        color: {COLOR_TEXTO_CUERPO};
        background-color: {COLOR_FONDO};
    }}

    QLabel {{
        background: transparent;
    }}

    QLabel#titulo_grande {{
        font-size: {h1_size};
        font-weight: bold;
        color: {COLOR_TEXTO_TITULO};
    }}

    QLabel#subtitulo {{
        font-size: {h2_size};
        font-weight: 600;
        color: {COLOR_PRIMARIO};
    }}

    /* Tarjetas y Contenedores */
    QFrame#tarjeta {{
        background-color: {COLOR_SUPERFICIE};
        border: 1px solid {COLOR_BORDE};
        border-radius: 14px;
        padding: 16px;
    }}

    QFrame#tarjeta_destacada {{
        background-color: #EEF2FF;
        border: 2px solid #C7D2FE;
        border-radius: 14px;
        padding: 18px;
    }}

    /* Botones Modernos */
    QPushButton {{
        background-color: {COLOR_PRIMARIO};
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        min-height: 24px;
    }}

    QPushButton:hover {{
        background-color: {COLOR_PRIMARIO_HOVER};
    }}

    QPushButton:pressed {{
        background-color: #3730A3;
    }}

    QPushButton:disabled {{
        background-color: #CBD5E1;
        color: #94A3B8;
    }}

    QPushButton#btn_secundario {{
        background-color: #F1F5F9;
        color: {COLOR_TEXTO_TITULO};
        border: 1px solid {COLOR_BORDE};
    }}

    QPushButton#btn_secundario:hover {{
        background-color: #E2E8F0;
    }}

    QPushButton#btn_exito {{
        background-color: {COLOR_EXITO};
        color: white;
    }}

    QPushButton#btn_exito:hover {{
        background-color: #059669;
    }}

    QPushButton#btn_padre {{
        background-color: transparent;
        color: #94A3B8;
        border: 1px dashed #CBD5E1;
        font-size: 12px;
        padding: 6px 12px;
    }}

    QPushButton#btn_padre:hover {{
        color: {COLOR_TEXTO_TITULO};
        border-color: #94A3B8;
    }}

    /* Entradas de texto */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {COLOR_SUPERFICIE};
        border: 1px solid {COLOR_BORDE};
        border-radius: 8px;
        padding: 8px 12px;
        color: {COLOR_TEXTO_TITULO};
    }}

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border: 2px solid {COLOR_PRIMARIO};
    }}

    /* Scrollbars suaves */
    QScrollBar:vertical {{
        background: {COLOR_FONDO};
        width: 10px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical {{
        background: #CBD5E1;
        border-radius: 5px;
        min-height: 20px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: #94A3B8;
    }}

    /* Pestañas */
    QTabWidget::pane {{
        border: 1px solid {COLOR_BORDE};
        background: {COLOR_SUPERFICIE};
        border-radius: 12px;
    }}

    QTabBar::tab {{
        background: #F1F5F9;
        color: {COLOR_TEXTO_CUERPO};
        padding: 10px 18px;
        margin-right: 4px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 600;
    }}

    QTabBar::tab:selected {{
        background: {COLOR_SUPERFICIE};
        color: {COLOR_PRIMARIO};
        border-bottom: 2px solid {COLOR_PRIMARIO};
    }}
    """

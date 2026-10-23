"""
Generador de Cuadernillos Imprimibles y Hojas de Respuestas de Burbujas.
Permite imprimir en papel evaluaciones tipo ICFES Saber 7.° para practicar con lápiz y papel.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from ..config.configuracion import obtener_ruta_datos

logger = logging.getLogger(__name__)


class GeneradorImprimibleICFES:
    """Crea documentos HTML listos para imprimir o guardar como PDF en cualquier navegador."""

    @classmethod
    def generar_cuadernillo_html(
        cls,
        lectura: Dict[str, Any],
        preguntas: List[Dict[str, Any]],
        ruta_salida: Optional[Path] = None,
    ) -> Path:
        if ruta_salida is None:
            carpeta = obtener_ruta_datos() / "cuadernillos_impresion"
            carpeta.mkdir(parents=True, exist_ok=True)
            slug = lectura.get("id", "prueba")
            ruta_salida = carpeta / f"Cuadernillo_ICFES_{slug}.html"

        titulo = lectura.get("titulo", "Lectura Crítica")
        tipo_texto = lectura.get("tipo_texto", "Continuo").capitalize()
        texto = lectura.get("texto", "").replace("\n\n", "</p><p>").replace("\n", "<br>")

        # Construir HTML de preguntas
        preguntas_html = ""
        for i, p in enumerate(preguntas):
            opciones_html = ""
            letras = ["A", "B", "C", "D"]
            for j, opt in enumerate(p.get("opciones", [])):
                opciones_html += f"""
                <div class="opcion">
                    <span class="letra-circulo">{letras[j]}</span> {opt}
                </div>
                """
            dim = p.get("nivel", "literal").capitalize()
            preguntas_html += f"""
            <div class="bloque-pregunta">
                <div class="pregunta-cabecera">
                    <strong>Pregunta {i + 1}</strong> <span class="tag-dim">[Dimensión: {dim}]</span>
                </div>
                <div class="enunciado">{p.get('enunciado', '')}</div>
                <div class="opciones-lista">{opciones_html}</div>
            </div>
            """

        # Construir Hoja de Respuestas de Burbujas
        filas_burbujas = ""
        for i in range(len(preguntas)):
            filas_burbujas += f"""
            <div class="fila-burbuja">
                <span class="num-b">{i + 1:02d}</span>
                <span class="burbuja">A</span>
                <span class="burbuja">B</span>
                <span class="burbuja">C</span>
                <span class="burbuja">D</span>
            </div>
            """

        # Clave de respuestas al final para el padre
        clave_filas = ""
        for i, p in enumerate(preguntas):
            letras = ["A", "B", "C", "D"]
            c_letra = letras[p.get("correcta", 0)]
            clave_filas += f"<li><strong>Pregunta {i + 1}:</strong> Opción {c_letra} — <i>{p.get('explicacion', '')}</i></li>"

        html_completo = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Cuadernillo Saber 7.° — {titulo}</title>
<style>
    @page {{
        size: letter;
        margin: 15mm;
    }}
    body {{
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #111827;
        line-height: 1.5;
        font-size: 13px;
        background: #FFFFFF;
        margin: 0;
        padding: 0;
    }}
    .encabezado {{
        border-bottom: 2px solid #000;
        padding-bottom: 10px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .titulo-inst {{
        font-size: 15px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .sub-inst {{
        font-size: 11px;
        color: #4B5563;
    }}
    .datos-estudiante {{
        display: grid;
        grid-template-columns: 2fr 1fr 1fr;
        gap: 10px;
        margin-bottom: 15px;
        border: 1px dashed #9CA3AF;
        padding: 8px;
        font-size: 11px;
    }}
    .caja-texto {{
        background: #F9FAFB;
        border: 1px solid #D1D5DB;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 20px;
        text-align: justify;
    }}
    .titulo-lectura {{
        font-size: 16px;
        font-weight: bold;
        margin-top: 0;
        color: #1E3A8A;
        border-bottom: 1px solid #E5E7EB;
        padding-bottom: 4px;
    }}
    .bloque-pregunta {{
        page-break-inside: avoid;
        margin-bottom: 16px;
        border-bottom: 1px dotted #E5E7EB;
        padding-bottom: 12px;
    }}
    .pregunta-cabecera {{
        font-size: 12px;
        margin-bottom: 4px;
    }}
    .tag-dim {{
        font-size: 10px;
        color: #6B7280;
        font-weight: normal;
    }}
    .enunciado {{
        font-weight: 600;
        font-size: 13px;
        margin-bottom: 8px;
    }}
    .opcion {{
        margin-bottom: 5px;
        display: flex;
        align-items: center;
    }}
    .letra-circulo {{
        display: inline-block;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        border: 1px solid #374151;
        text-align: center;
        line-height: 18px;
        font-size: 11px;
        font-weight: bold;
        margin-right: 8px;
    }}
    .salto-pagina {{
        page-break-before: always;
    }}
    .hoja-respuestas {{
        border: 2px solid #111827;
        padding: 20px;
        border-radius: 8px;
        max-width: 480px;
        margin: 20px auto;
    }}
    .fila-burbuja {{
        display: flex;
        align-items: center;
        justify-content: space-around;
        padding: 6px 0;
        border-bottom: 1px solid #F3F4F6;
    }}
    .num-b {{
        font-weight: bold;
        width: 30px;
    }}
    .burbuja {{
        display: inline-block;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        border: 1.5px solid #1F2937;
        text-align: center;
        line-height: 26px;
        font-weight: bold;
        font-size: 12px;
    }}
    .clave-padre {{
        background: #FEF3C7;
        border: 1px solid #F59E0B;
        padding: 15px;
        border-radius: 8px;
        margin-top: 30px;
    }}
    @media print {{
        .no-imprimir {{ display: none; }}
    }}
</style>
</head>
<body>

<div class="no-imprimir" style="background:#EEF2FF; border:1px solid #C7D2FE; padding:10px; margin-bottom:15px; text-align:center;">
    <strong>📄 Vista previa de impresión:</strong> Presiona <code>Ctrl + P</code> en tu navegador para imprimir o guardar como PDF.
</div>

<div class="encabezado">
    <div>
        <div class="titulo-inst">Evaluación Diagnóstica — Lectura Crítica Saber 7.°</div>
        <div class="sub-inst">Programa de Fortalecimiento Lector Lee y Juega • República de Colombia</div>
    </div>
    <div style="font-weight:bold; font-size:14px; text-align:right;">
        Cuadernillo ICFES<br><small style="color:#6B7280;">Nivel Formativo</small>
    </div>
</div>

<div class="datos-estudiante">
    <div><strong>Nombre de la estudiante:</strong> ________________________________________</div>
    <div><strong>Grado:</strong> 7.° Bachillerato</div>
    <div><strong>Fecha:</strong> ____/____/2026</div>
</div>

<div class="caja-texto">
    <h2 class="titulo-lectura">{titulo}</h2>
    <p><strong>Tipo de texto:</strong> {tipo_texto}</p>
    <p>{texto}</p>
</div>

<h3>Cuestionario de Preguntas</h3>
{preguntas_html}

<div class="salto-pagina"></div>

<div class="encabezado">
    <div class="titulo-inst">Hoja Oficial de Respuestas — Lectura Crítica</div>
    <div class="sub-inst">Rellene completamente los círculos con lápiz de mina negra N.° 2</div>
</div>

<div class="hoja-respuestas">
    <div style="text-align:center; font-weight:bold; margin-bottom:10px;">SECCIÓN DE BURBUJAS DE RESPUESTA</div>
    {filas_burbujas}
</div>

<div class="salto-pagina"></div>

<div class="clave-padre">
    <h3 style="margin-top:0; color:#B45309;">🔐 Clave de Respuestas y Explicaciones (Para el Padre o Tutor)</h3>
    <p style="font-size:12px;">Utiliza esta guía para calificar el cuadernillo resuelto en papel y retroalimentar a tu hija:</p>
    <ul style="padding-left:20px; font-size:12px;">
        {clave_filas}
    </ul>
</div>

</body>
</html>
"""
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(html_completo)

        logger.info(f"Cuadernillo imprimible generado en: {ruta_salida}")
        return ruta_salida

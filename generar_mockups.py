"""
Generador de capturas y mockups visuales para el README de Lee y Juega.
Crea imágenes de alta definición estilo showcase comercial.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont

CARPETA_ASSETS = Path(__file__).resolve().parent / "assets"
CARPETA_ASSETS.mkdir(parents=True, exist_ok=True)


def crear_banner_hero():
    """Genera el banner principal estilo Guionaria."""
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), color="#0F172A")
    draw = ImageDraw.Draw(img)

    # Fondo con degradado o acentos modernos
    for i in range(h):
        # Gradiente suave de pizarra profundo a azul medianoche
        ratio = i / h
        r = int(15 * (1 - ratio) + 10 * ratio)
        g = int(23 * (1 - ratio) + 15 * ratio)
        b = int(42 * (1 - ratio) + 30 * ratio)
        draw.line([(0, i), (w, i)], fill=(r, g, b))

    # Glow sutil indigo en esquina inferior izquierda
    draw.ellipse([-100, 300, 500, 800], fill="#1E1B4B")
    draw.ellipse([-50, 350, 450, 750], fill="#312E81")

    # Intentar cargar fuentes estándar de Windows
    try:
        font_logo = ImageFont.truetype("segoeui.ttf", 36)
        font_tag = ImageFont.truetype("segoeuib.ttf", 44)
        font_sub = ImageFont.truetype("segoeui.ttf", 20)
        font_pill = ImageFont.truetype("segoeuib.ttf", 15)
        font_app_title = ImageFont.truetype("segoeuib.ttf", 22)
        font_app_text = ImageFont.truetype("segoeui.ttf", 14)
    except Exception:
        font_logo = ImageFont.load_default()
        font_tag = font_logo
        font_sub = font_logo
        font_pill = font_logo
        font_app_title = font_logo
        font_app_text = font_logo

    # 1. Lado Izquierdo: Branding y Textos
    # Badge Logo
    draw.rounded_rectangle([70, 70, 290, 120], radius=12, fill="#4F46E5")
    draw.text((85, 78), "📖 Lee y Juega", font=font_logo, fill="#FFFFFF")

    # Título Principal Impactante
    draw.text((70, 160), "De la lectura al juego,\nganado con mérito.", font=font_tag, fill="#F8FAFC", spacing=10)

    # Subtítulo explicativo
    sub_desc = (
        "Plataforma educativa con bloqueo tipo kiosco\n"
        "para aprender Lectura Crítica (ICFES) en 7.º grado.\n"
        "Todo en tu computador, autónomo y 100% privado."
    )
    draw.text((70, 290), sub_desc, font=font_sub, fill="#94A3B8", spacing=6)

    # Pills de valor clave
    pills = [
        ("✔ Windows 10/11", "#0284C7"),
        ("✔ ICFES Colombia", "#10B981"),
        ("✔ 100% Local & Seguro", "#6366F1"),
    ]
    x_pill = 70
    for texto, color_bg in pills:
        draw.rounded_rectangle([x_pill, 430, x_pill + 160, 470], radius=20, fill=color_bg)
        draw.text((x_pill + 15, 440), texto, font=font_pill, fill="#FFFFFF")
        x_pill += 175

    # 2. Lado Derecho: Mockup de la Ventana Kiosco
    # Marco de ventana estilo monitor / app flotante
    wx0, wy0, wx1, wy1 = 620, 70, 1140, 560
    # Sombra
    draw.rounded_rectangle([wx0 + 10, wy0 + 10, wx1 + 10, wy1 + 10], radius=16, fill="#020617")
    # Ventana principal
    draw.rounded_rectangle([wx0, wy0, wx1, wy1], radius=16, fill="#FFFFFF")

    # Barra superior de la app
    draw.rounded_rectangle([wx0, wy0, wx1, wy0 + 55], radius=16, fill="#F8FAFC")
    draw.line([(wx0, wy0 + 55), (wx1, wy0 + 55)], fill="#E2E8F0", width=1)
    draw.text((wx0 + 20, wy0 + 16), "📖 Lee y Juega — Pantalla de Bloqueo Kiosco", font=font_app_title, fill="#1E293B")
    draw.text((wx1 - 130, wy0 + 20), "🔐 Modo Padre", font=font_app_text, fill="#64748B")

    # Contenido de la ventana simulada:
    # Tarjeta de bienvenida
    cx0, cy0, cx1, cy1 = wx0 + 35, wy0 + 80, wx1 - 35, wy1 - 40
    draw.rounded_rectangle([cx0, cy0, cx1, cy1], radius=12, fill="#F8FAFC", outline="#CBD5E1", width=1)

    draw.text((cx0 + 25, cy0 + 20), "¡Hola, campeona! Tu tiempo de ocio terminó.", font=font_app_title, fill="#0F172A")
    draw.text((cx0 + 25, cy0 + 55), "Lee este texto del Nivel 2 y aprueba el test para ganar +60 minutos:", font=font_app_text, fill="#475569")

    # Tarjeta métricas
    mx0, my0, mx1, my1 = cx0 + 25, cy0 + 90, cx1 - 25, cy0 + 140
    draw.rounded_rectangle([mx0, my0, mx1, my1], radius=8, fill="#EEF2FF", outline="#C7D2FE", width=1)
    draw.text((mx0 + 15, my0 + 15), "🎯 Nivel Actual: 2   •   🎁 Recompensa: +60 min   •   🔥 Racha: 4 días", font=font_app_text, fill="#4338CA")

    # Caja de lectura simulada
    lx0, ly0, lx1, ly1 = cx0 + 25, cy0 + 155, cx1 - 25, cy0 + 310
    draw.rounded_rectangle([lx0, ly0, lx1, ly1], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((lx0 + 15, ly0 + 12), "Las ballenas jorobadas en el Pacífico colombiano", font=font_app_title, fill="#0369A1")
    texto_parrafo = (
        "Cada año, entre julio y octubre, las aguas del Parque Utría y el golfo de Tribugá\n"
        "en el Chocó reciben la migración de ballenas jorobadas desde la Antártida...\n\n"
        "Pregunta 1 de 5 [Dimensión ICFES: Inferencial]:\n"
        "¿Por qué viajan más de 8.500 km para dar a luz en aguas colombianas?"
    )
    draw.text((lx0 + 15, ly0 + 45), texto_parrafo, font=font_app_text, fill="#334155", spacing=4)

    # Botón de acción simulado
    bx0, by0, bx1, by1 = cx0 + 80, cy0 + 330, cx1 - 80, cy0 + 375
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=10, fill="#10B981")
    draw.text((bx0 + 45, by0 + 12), "✍️ Iniciar Test de Comprensión (5 Preguntas)", font=font_app_text, fill="#FFFFFF")

    ruta_salida = CARPETA_ASSETS / "hero_banner.png"
    img.save(ruta_salida, quality=95)
    print(f"Hero banner guardado en: {ruta_salida}")


def crear_captura_modo_padre():
    """Genera captura ilustrativa del Modo Padre con dashboard y gráficas."""
    w, h = 900, 520
    img = Image.new("RGB", (w, h), color="#F8FAFC")
    draw = ImageDraw.Draw(img)

    try:
        font_h1 = ImageFont.truetype("segoeuib.ttf", 22)
        font_h2 = ImageFont.truetype("segoeuib.ttf", 16)
        font_body = ImageFont.truetype("segoeui.ttf", 13)
        font_stat_val = ImageFont.truetype("segoeuib.ttf", 24)
    except Exception:
        font_h1 = ImageFont.load_default()
        font_h2 = font_h1
        font_body = font_h1
        font_stat_val = font_h1

    # Barra superior
    draw.rectangle([0, 0, w, 60], fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((30, 18), "🔐 Lee y Juega — Panel de Control del Padre", font=font_h1, fill="#1E293B")
    draw.rounded_rectangle([w - 140, 14, w - 30, 46], radius=6, fill="#F1F5F9", outline="#CBD5E1")
    draw.text((w - 120, 22), "Cerrar Panel", font=font_body, fill="#334155")

    # Tabs
    tabs = ["⚙️ Configuración", "📊 Estadísticas y Progreso (Activa)", "⚡ Acciones y Control"]
    tx = 30
    for i, t in enumerate(tabs):
        color_bg = "#FFFFFF" if i == 1 else "#E2E8F0"
        color_fg = "#4F46E5" if i == 1 else "#64748B"
        draw.rounded_rectangle([tx, 75, tx + 200, 105], radius=6, fill=color_bg)
        draw.text((tx + 12, 82), t, font=font_body, fill=color_fg)
        tx += 210

    # 4 Tarjetas de Métricas
    stats = [
        ("Tests Aprobados", "18 de 21", "#ECFDF5", "#047857"),
        ("Tasa de Aprobación", "85.7 %", "#EEF2FF", "#4338CA"),
        ("Nivel Actual", "Nivel 3 (ICFES)", "#FEF3C7", "#B45309"),
        ("Racha de Días", "6 Días seguidos", "#FCE7F3", "#BE185D"),
    ]
    sx = 30
    for tit, val, bg, fg in stats:
        draw.rounded_rectangle([sx, 120, sx + 195, 195], radius=10, fill=bg)
        draw.text((sx + 15, 130), tit, font=font_body, fill=fg)
        draw.text((sx + 15, 150), val, font=font_stat_val, fill=fg)
        sx += 215

    # Contenedor Gráfica Semanal
    draw.rounded_rectangle([30, 215, w - 30, 485], radius=12, fill="#FFFFFF", outline="#CBD5E1", width=1)
    draw.text((50, 230), "Balance Semanal: Minutos de Lectura Ganados vs. Tiempo Recreativo Jugado", font=font_h2, fill="#1E293B")

    # Barras simuladas de la gráfica
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    ganados = [60, 60, 120, 60, 90, 120, 60]
    gastados = [55, 45, 110, 50, 85, 115, 40]
    
    bx = 80
    base_y = 440
    for i, d in enumerate(dias):
        # Barra ganados (Verde)
        h_g = int(ganados[i] * 1.3)
        draw.rectangle([bx, base_y - h_g, bx + 30, base_y], fill="#10B981")
        # Barra gastados (Ámbar)
        h_j = int(gastados[i] * 1.3)
        draw.rectangle([bx + 35, base_y - h_j, bx + 65, base_y], fill="#F59E0B")

        draw.text((bx + 12, base_y + 10), d[:3], font=font_body, fill="#64748B")
        bx += 110

    # Leyenda
    draw.rectangle([w - 320, 235, w - 305, 250], fill="#10B981")
    draw.text((w - 295, 235), "Minutos Ganados", font=font_body, fill="#334155")
    draw.rectangle([w - 180, 235, w - 165, 250], fill="#F59E0B")
    draw.text((w - 155, 235), "Minutos Jugados", font=font_body, fill="#334155")

    ruta_salida = CARPETA_ASSETS / "pantalla_modo_padre.png"
    img.save(ruta_salida, quality=95)
    print(f"Modo padre captura guardada en: {ruta_salida}")


def crear_captura_test_icfes():
    """Genera captura del módulo de evaluación interactiva con retroalimentación."""
    w, h = 900, 520
    img = Image.new("RGB", (w, h), color="#F8FAFC")
    draw = ImageDraw.Draw(img)

    try:
        font_h1 = ImageFont.truetype("segoeuib.ttf", 20)
        font_body = ImageFont.truetype("segoeui.ttf", 14)
        font_opt = ImageFont.truetype("segoeui.ttf", 13)
        font_badge = ImageFont.truetype("segoeuib.ttf", 12)
    except Exception:
        font_h1 = ImageFont.load_default()
        font_body = font_h1
        font_opt = font_h1
        font_badge = font_h1

    # Header
    draw.rectangle([0, 0, w, 55], fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((30, 16), "Pregunta 3 de 5  •  Test de Lectura Crítica", font=font_h1, fill="#1E293B")
    draw.rounded_rectangle([w - 180, 12, w - 30, 44], radius=6, fill="#EEF2FF", outline="#C7D2FE")
    draw.text((w - 165, 18), "📖 Releer el texto", font=font_body, fill="#4338CA")

    # Barra de progreso
    draw.rectangle([0, 55, w, 61], fill="#E2E8F0")
    draw.rectangle([0, 55, int(w * 0.6), 61], fill="#4F46E5")

    # Tarjeta de pregunta
    draw.rounded_rectangle([30, 85, w - 30, 480], radius=14, fill="#FFFFFF", outline="#CBD5E1", width=1)

    # Dimensión Badge
    draw.rounded_rectangle([55, 105, 230, 135], radius=6, fill="#EEF2FF")
    draw.text((68, 112), "Dimensión ICFES: Crítico", font=font_badge, fill="#4F46E5")

    # Enunciado
    enun = (
        "¿Cuál de las siguientes afirmaciones del texto constituye una OPINIÓN subjetiva\n"
        "y NO un dato científicamente comprobable?"
    )
    draw.text((55, 155), enun, font=font_h1, fill="#0F172A", spacing=4)

    # Opciones de respuesta
    opciones = [
        ("A", "Las ballenas jorobadas viajan más de 8.500 km desde la Antártida hasta Colombia.", False),
        ("B", "Las aguas del Chocó son las más hermosas, mágicas y acogedoras de todo el planeta.", True),
        ("C", "Las crías recién nacidas no poseen una capa de grasa suficiente para sobrevivir al polo sur.", False),
        ("D", "Los machos emiten cantos submarinos de cortejo durante la temporada de apareamiento.", False),
    ]

    oy = 230
    for letra, texto, seleccionada in opciones:
        bg_col = "#ECFDF5" if seleccionada else "#F8FAFC"
        border_col = "#10B981" if seleccionada else "#E2E8F0"
        draw.rounded_rectangle([55, oy, w - 55, oy + 42], radius=8, fill=bg_col, outline=border_col, width=2 if seleccionada else 1)
        # Radio circle
        draw.ellipse([70, oy + 12, 88, oy + 30], fill="#10B981" if seleccionada else "#FFFFFF", outline="#10B981" if seleccionada else "#94A3B8")
        if seleccionada:
            draw.ellipse([75, oy + 17, 83, oy + 25], fill="#FFFFFF")
        draw.text((105, oy + 12), f"{letra})  {texto}", font=font_opt, fill="#0F172A")
        oy += 52

    # Botones inferiores
    draw.rounded_rectangle([55, 430, 160, 465], radius=8, fill="#F1F5F9", outline="#CBD5E1")
    draw.text((75, 438), "← Anterior", font=font_body, fill="#334155")

    draw.rounded_rectangle([w - 180, 430, w - 55, 465], radius=8, fill="#4F46E5")
    draw.text((w - 160, 438), "Siguiente →", font=font_body, fill="#FFFFFF")

    ruta_salida = CARPETA_ASSETS / "pantalla_test_icfes.png"
    img.save(ruta_salida, quality=95)
    print(f"Test ICFES captura guardada en: {ruta_salida}")


if __name__ == "__main__":
    crear_banner_hero()
    crear_captura_modo_padre()
    crear_captura_test_icfes()

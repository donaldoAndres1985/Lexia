# Especificación: "Lee y Juega" — app educativa de Lectura Crítica con bloqueo tipo kiosco

Este documento rige la arquitectura, diseño y requisitos de implementación del proyecto.

## 0. Rol y objetivo
Aplicación de escritorio para **Windows 10/11** llamada **"Lee y Juega"**.
**Propósito:** que una niña de 12 años, en **7.º grado** en Colombia, aprenda a leer como exige la prueba de **Lectura Crítica del ICFES**. En su computador, cuando se le acaba el tiempo de ocio ganado, la app muestra una **pantalla completa que se pone encima de todas las ventanas** y no la deja seguir en el juego o el video hasta que **lee un texto de su nivel y aprueba un test** (unos 20 minutos). Aprobar le da **tiempo de recompensa** configurable (por defecto 60 minutos). Hay un **modo padre** con clave para configurar todo y ver estadísticas.

**Requisitos transversales:**
- Todo en **español**: interfaz, textos, mensajes y comentarios del código.
- Solo tecnologías **gratuitas y de código abierto**.
- Todo **configurable** desde el modo padre.
- Calidad profesional: arquitectura limpia, manejo de errores, logs, pruebas e instalador.
- Interfaz **amigable, moderna y motivadora** para una niña de 12 años.
- **Importante sobre el bloqueo:** la app NO debe interceptar ni bloquear Ctrl+Alt+Supr, no debe ocultarse del sistema ni evadir al antivirus. El bloqueo es una **ventana kiosco a pantalla completa, siempre visible y siempre encima**, más la integración con el control parental de Windows (sección 8) como refuerzo. Debe ser desinstalable por el padre y por el administrador del equipo.

## 1. Tecnología
- Python 3.12
- PySide6 (Qt 6) con hojas de estilo QSS
- pywin32 (DPAPI, ventanas activas, inicio de Windows)
- psutil
- SQLite + SQLAlchemy
- argon2-cffi
- httpx + trafilatura
- API Gemini (google-genai / httpx fallback) + respaldo offline
- matplotlib (gráficos de estadísticas y textos discontinuos)
- PyInstaller + Inno Setup
- pytest + pytest-qt

## 2. Estructura de carpetas
- `lee_y_juega/`: paquete principal
- `recursos/banco_offline/`: mínimo 40 lecturas con preguntas estructuradas
- `recursos/lecciones/`: contenido pedagógico interactivo
- `instalador/`: scripts de empaquetado
- `tests/`: suite de pruebas automatizadas
- `docs/`: manuales y especificaciones

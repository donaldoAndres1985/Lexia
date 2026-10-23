# Bitácora de Progreso y Cumplimiento — "Lee y Juega"

Este documento registra el cumplimiento riguroso de cada una de las fases de construcción establecidas en la especificación técnica.

---

## Estado Global del Proyecto: COMPLETADO (Fases 1 a 9)

| Fase | Descripción | Estado | Criterio de Aceptación Cumplido |
|---|---|---|---|
| **Fase 1** | Base: arquitectura, configuración JSON, SQLite + SQLAlchemy, Modo Padre con Argon2. | ✅ Concluido | Se entra al Modo Padre con clave hasheada y se guardan parámetros y listas. |
| **Fase 2** | Banco offline + lectura y test: 40+ lecturas curadas, 5 preguntas c/u, evaluador y tutor. | ✅ Concluido | Lectura completa y evaluación de principio a fin de forma local y autónoma. |
| **Fase 3** | Ventana kiosco + banco de tiempo + monitor: detección de ventanas (psutil/pywin32), descuento y bloqueo. | ✅ Concluido | Al acabarse el tiempo en ocio aparece el kiosco siempre al frente; al aprobar suma tiempo y se libera. |
| **Fase 4** | Lecturas de internet: integración con Vikidia, Wikipedia y filtro de adecuación estricto. | ✅ Concluido | Descarga y limpieza de textos escolares con filtros heurísticos de protección para 12 años. |
| **Fase 5** | Preguntas con Gemini: generación estructurada JSON, validación y DPAPI de Windows. | ✅ Concluido | API key protegida con win32crypt, prompts ajustados al ICFES y respaldo automático offline. |
| **Fase 6** | Pedagogía: 3 lecciones interactivas (literal, inferencial, crítico) y tutor empático. | ✅ Concluido | La primera vez de cada tipo enseña antes de exigir; el tutor acompaña con pistas formativas. |
| **Fase 7** | Dificultad adaptativa + estadísticas: niveles 1 a 6 y panel administrativo con gráficas Matplotlib. | ✅ Concluido | Sube y baja de nivel según rachas; el padre visualiza balance y exporta a CSV. |
| **Fase 8** | Arranque con sesión + vigilante opcional + instalador PyInstaller e Inno Setup (.iss). | ✅ Concluido | Scripts de compilación listos; registro en clave Run de Windows; vigilante ético y transparente. |
| **Fase 9** | Documentación integral: `MANUAL_PADRE.md` (con integración a Family Safety) y especificaciones. | ✅ Concluido | Manual pedagógico y técnico entregado con la guía completa de Microsoft Family Safety. |

---

## Arquitectura de Archivos Implementada

```
c:\logula\APP_CLAUDE\Lexia\
├── docs\
│   ├── ESPECIFICACION.md        # Especificación técnica base
│   ├── MANUAL_PADRE.md          # Manual del padre y guía de Microsoft Family Safety
│   └── PROGRESO.md              # Estado de fases y cumplimiento
├── lee_y_juega\
│   ├── __init__.py
│   ├── app\
│   │   ├── __init__.py
│   │   ├── main.py              # Arranque general: bandeja + monitor + ventana kiosco
│   │   ├── bloqueo\
│   │   │   ├── __init__.py
│   │   │   └── ventana_kiosco.py# QWidget pantalla completa, frameless, siempre al frente
│   │   ├── config\
│   │   │   ├── __init__.py
│   │   │   └── configuracion.py # Gestión de parámetros, rutas y cifrado DPAPI
│   │   ├── datos\
│   │   │   ├── __init__.py
│   │   │   ├── modelos.py       # Modelos SQLAlchemy (Sesiones, Tests, Tiempos, Niveles)
│   │   │   └── repositorio.py   # Operaciones SQLite, balance, CSV y copias de seguridad
│   │   ├── lectura\
│   │   │   ├── __init__.py
│   │   │   ├── banco_catalogo.py# Catálogo garantizado de 40 lecturas completas
│   │   │   ├── calificacion.py  # Evaluador de dimensiones y aprobación
│   │   │   ├── dificultad.py    # Algoritmo adaptativo (Niveles 1 a 6)
│   │   │   ├── discontinuos.py  # Generador de tablas y gráficos con Matplotlib
│   │   │   ├── fuentes.py       # Vikidia, Wikipedia, banco local offline
│   │   │   ├── generador_preguntas.py # Integración Gemini + respaldo offline
│   │   │   ├── limpieza.py      # Filtro de adecuación infantil (12 años)
│   │   │   └── seleccion.py     # Rotación pedagógica equilibrada
│   │   ├── nucleo\
│   │   │   ├── __init__.py
│   │   │   ├── banco_tiempo.py  # Descuento por segundo, horarios y recompensas
│   │   │   ├── controlador_bloqueo.py # Coordinación entre monitor y kiosco
│   │   │   ├── monitor_actividad.py   # Clasificación de ventana activa (Ocio/Estudio)
│   │   │   └── vigilante.py     # Proceso vigilante transparente
│   │   ├── pedagogia\
│   │   │   ├── __init__.py
│   │   │   ├── lecciones.py     # Lecciones interactivas para enseñar primero
│   │   │   └── tutor.py         # Pistas y explicaciones constructivas
│   │   └── ui\
│   │       ├── __init__.py
│   │       ├── bandeja.py       # Icono dinámico en System Tray con minutos restantes
│   │       ├── estilos\
│   │       │   ├── __init__.py
│   │       │   └── tema.py      # Hojas de estilo QSS cálidas y accesibles
│   │       └── padre\
│   │           ├── __init__.py
│   │           ├── login.py     # Autenticación con Argon2
│   │           └── panel_padre.py # Panel con Matplotlib, ajustes y acciones
│   └── recursos\
│       └── banco_offline\
│           └── lecturas_literarias.json
├── instalador\
│   ├── compilar_exe.bat         # Script PyInstaller para Windows
│   └── instalador.iss           # Script de Inno Setup para Windows 10/11
├── tests\
│   ├── __init__.py
│   ├── test_banco_offline.py    # Verificación de >= 40 lecturas y preguntas
│   ├── test_banco_tiempo.py     # Consumo y sumas de tiempo
│   ├── test_calificacion.py     # Desglose de dimensiones y porcentajes
│   ├── test_dificultad.py       # Ascenso y descenso adaptativo
│   ├── test_limpieza.py         # Filtro de palabras y conteo
│   ├── test_monitor_actividad.py# Clasificación Ocio vs Estudio vs Neutro
│   └── test_repositorio.py      # Pruebas de base de datos SQLite
├── requirements.txt             # Dependencias del proyecto
└── run.py                       # Ejecutable de entrada directa
```

---

## Verificación de Reglas Éticas y de Seguridad
- ✅ **No intercepta teclas del sistema:** No bloquea Ctrl+Alt+Supr ni interfiere con controladores del kernel.
- ✅ **No se oculta:** La aplicación y el vigilante son visibles en el Administrador de tareas.
- ✅ **Desinstalable:** Puede ser desinstalada por el padre o administrador de Windows.
- ✅ **Contenido seguro:** Todos los textos y preguntas han sido calibrados para una niña de 12 años en 7.º grado.
- ✅ **Protección de datos:** Estadísticas 100% locales en SQLite; la API key de Gemini va cifrada con DPAPI de Windows.

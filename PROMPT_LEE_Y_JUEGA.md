# Prompt para construir "Lee y Juega" — app educativa de Lectura Crítica con bloqueo tipo kiosco

> Copia todo este documento y pásalo al agente (Antigravity + Gemini). Si trabaja sobre una carpeta, guárdalo como `docs/ESPECIFICACION.md` y dile: "Lee docs/ESPECIFICACION.md y construye la aplicación completa fase por fase, cumpliendo cada sección."

---

## 0. Rol y objetivo

Eres un ingeniero de software senior y diseñador instruccional. Construye, de punta a punta, una aplicación de escritorio para **Windows 10/11** llamada **"Lee y Juega"**.

**Propósito:** que una niña de 12 años, en **7.º grado** en Colombia, aprenda a leer como exige la prueba de **Lectura Crítica del ICFES**. En su computador, cuando se le acaba el tiempo de ocio ganado, la app muestra una **pantalla completa que se pone encima de todas las ventanas** y no la deja seguir en el juego o el video hasta que **lee un texto de su nivel y aprueba un test** (unos 20 minutos). Aprobar le da **tiempo de recompensa** configurable (por defecto 60 minutos). Hay un **modo padre** con clave para configurar todo y ver estadísticas.

**Requisitos transversales:**
- Todo en **español**: interfaz, textos, mensajes y comentarios del código.
- Solo tecnologías **gratuitas y de código abierto**.
- Todo **configurable** desde el modo padre.
- Calidad profesional: arquitectura limpia, manejo de errores, logs, pruebas e instalador.
- Interfaz **amigable, moderna y motivadora** para una niña de 12 años.
- **Importante sobre el bloqueo:** la app NO debe interceptar ni bloquear Ctrl+Alt+Supr, no debe ocultarse del sistema ni evadir al antivirus. El bloqueo es una **ventana kiosco a pantalla completa, siempre visible y siempre encima**, más la integración con el control parental de Windows (sección 8) como refuerzo. Debe ser desinstalable por el padre y por el administrador del equipo.

---

## 1. Tecnología (ya decidida)

| Componente | Tecnología | Motivo |
|---|---|---|
| Lenguaje | **Python 3.12** | Gratis, maduro, buen acceso a Windows |
| Interfaz | **PySide6 (Qt 6)** con hojas de estilo QSS | Pantalla completa real, siempre-encima, aspecto moderno |
| API de Windows | **pywin32** | Ventana activa, procesos, inicio con la sesión |
| Procesos | **psutil** | Detectar qué app está usando |
| Base de datos | **SQLite** + **SQLAlchemy** | Estadísticas y configuración local |
| Clave del padre | **argon2-cffi** | Hash seguro de la contraseña |
| Lecturas de internet | **httpx** + **trafilatura** | Descargar y limpiar textos |
| Preguntas | **API de Gemini** (`google-genai`, capa gratuita) con **respaldo offline** | Tests de calidad adaptados al nivel |
| Textos discontinuos | **matplotlib** | Tablas, gráficas e infografías simples |
| Estadísticas | matplotlib embebido en Qt | Panel del padre |
| Empaquetado | **PyInstaller** + **Inno Setup** | Ejecutable e instalador gratuitos |
| Pruebas | **pytest** + **pytest-qt** | Unitarias y de interfaz |

La API key de Gemini se guarda cifrada con **DPAPI de Windows** (`win32crypt`), nunca en el código ni en texto plano.

---

## 2. Arquitectura

```
lee_y_juega/
  app/
    main.py                 # arranque: bandeja + monitor + ventana de bloqueo
    config/                 # configuración por defecto, carga y guardado
    nucleo/
      monitor_actividad.py  # clasifica la ventana activa: ocio / estudio / neutro
      banco_tiempo.py       # minutos ganados, consumo y horarios
      controlador_bloqueo.py# decide cuándo mostrar el kiosco
    bloqueo/
      ventana_kiosco.py     # QWidget a pantalla completa, frameless, siempre encima
    lectura/
      fuentes.py            # Vikidia, Wikipedia, Wikisource, banco local
      seleccion.py          # escoge texto por nivel, tipo y variedad
      limpieza.py           # limpia, valida longitud y adecuación
      discontinuos.py       # genera tablas/gráficas/infografías con matplotlib
      generador_preguntas.py# Gemini + validación + respaldo offline
      calificacion.py       # puntaje, aprobación, retroalimentación
      dificultad.py         # nivel adaptativo
    pedagogia/
      lecciones.py          # lecciones interactivas de cada tipo de lectura
      tutor.py              # pistas y explicaciones tras cada respuesta
    ui/
      bandeja.py            # ícono con el tiempo restante
      padre/                # panel administrador
      estilos/              # tema, fuentes, íconos
    datos/
      modelos.py            # SQLAlchemy
      repositorio.py
  recursos/
    banco_offline/          # mínimo 40 lecturas con preguntas ya hechas
    lecciones/
  instalador/
    instalador.iss
  tests/
  docs/
    MANUAL_PADRE.md
    PROGRESO.md
```

**Arranque:** la app se registra para **iniciar con la sesión de Windows** (carpeta Inicio o clave Run del usuario). Corre minimizada en la bandeja mostrando el tiempo restante. Opcional y configurable por el padre: un pequeño **proceso vigilante** que, si la app principal se cierra, la vuelve a abrir. El vigilante es visible y se detiene desde el modo padre; no se oculta ni se protege contra el sistema.

---

## 3. Lógica de bloqueo

### 3.1 Clasificación de la actividad (`monitor_actividad.py`)
Cada 3 segundos obtén la **ventana en primer plano** (título + proceso) y clasifícala:

- **OCIO** (consume el tiempo del banco):
  - Procesos: `RobloxPlayerBeta.exe` y juegos configurables.
  - Títulos de navegador que contengan: YouTube, TikTok, Instagram, Facebook, Roblox, Twitch, Netflix, Discord, X. (Lista editable.)
- **ESTUDIO** (no consume ni activa el bloqueo):
  - ChatGPT, Gemini, Classroom, Word, Excel, PowerPoint, Docs, Khan Academy, Wikipedia, Canva, plataformas del colegio. (Lista editable.)
  - Música en segundo plano (Spotify, YouTube Music) se permite.
- **NEUTRO:** todo lo demás. No consume ni bloquea.

### 3.2 Banco de tiempo (`banco_tiempo.py`)
- La niña empieza el día con los minutos de ocio que el padre configure (por defecto 0: debe ganárselos leyendo).
- Mientras la ventana activa sea **OCIO**, descuenta tiempo del banco.
- Al llegar a 0, el controlador muestra el kiosco.
- Aprobar un test **suma** los minutos de recompensa configurados.
- Respeta **horarios**: franjas donde no se puede ganar ni gastar tiempo (por ejemplo, horario de colegio o después de las 9 p. m.).

### 3.3 Ventana kiosco (`ventana_kiosco.py`)
Cuando toca bloquear:
- `QWidget` a **pantalla completa**, sin bordes (`Qt.FramelessWindowHint`), **siempre encima** (`Qt.WindowStaysOnTopHint`), en **todos los monitores**.
- Se **re-eleva** cada pocos cientos de milisegundos para quedar siempre al frente, y se reactiva si pierde el foco (sin bloquear teclas del sistema).
- Botón de cerrar y Alt+F4 desactivados **dentro de la ventana** (eso es normal en apps kiosco; no toca Ctrl+Alt+Supr ni el Administrador de tareas).
- Mientras está activa, no consume tiempo del banco.
- Se cierra sola **solo** cuando el test se aprueba, o cuando el padre entra con su clave.

> Limitación honesta que debes documentar en `MANUAL_PADRE.md`: una ventana kiosco se puede cerrar desde el Administrador de tareas. Por eso el padre debe activar además el control parental de Windows (sección 8), que sí impide el ocio a nivel de sistema. Los dos juntos hacen que cerrar la app no sirva de nada.

---

## 4. Flujo de la niña (pantalla de bloqueo)

1. **Bienvenida motivadora:** saludo, cuántos minutos gana si aprueba, su racha de días y su nivel actual.
2. **¿Primera vez en este tipo de lectura?** Si nunca ha visto ese tipo (literal, inferencial o crítico), primero una **lección corta** (sección 6). Si ya lo vio, pasa directo.
3. **Lectura:** se muestra el texto (continuo o discontinuo) de su nivel. Puede releer sin límite. Un temporizador suave, sin presión agobiante.
4. **Test:** 5 a 8 preguntas de opción múltiple que cubren los tres niveles de comprensión (sección 5).
5. **Resultado y retroalimentación:**
   - Si **aprueba** (umbral configurable, por defecto 70 %): felicitación, suma de minutos, y el kiosco se cierra.
   - Si **no aprueba:** le muestra, pregunta por pregunta, por qué la respuesta correcta lo es (el tutor explica), y le ofrece **otra lectura** para intentarlo de nuevo. Nunca la castiga ni la humilla; el tono es de entrenador.
6. Cada intento, apruebe o no, **se guarda** en estadísticas.

---

## 5. Motor de lectura y preguntas

### 5.1 Tipos de texto (como en el ICFES)
- **Continuos:**
  - Literarios: cuentos, fábulas, fragmentos de novela, poemas, mini-obras de teatro.
  - Informativos: textos expositivos, noticias, columnas de opinión sencillas, textos argumentativos.
- **Discontinuos:** tablas, gráficas de barras/líneas, infografías simples, avisos, caricaturas con texto. Genera estos con **matplotlib** a partir de datos, o toma infografías de dominio público.

La app **rota** entre tipos para que practique todos.

### 5.2 De dónde salen las lecturas (`fuentes.py`)
Prioriza fuentes **gratuitas, libres y apropiadas para menores**:
- **Vikidia** (enciclopedia para niños de 8 a 13 años, en español): ideal para 7.º grado.
- **Wikipedia en español** (artículos cortos), simplificando con el generador si hace falta.
- **Wikisource** para cuentos y fábulas clásicas de dominio público.
- **Banco local offline** (`recursos/banco_offline/`): mínimo **40 lecturas** ya curadas con sus preguntas, para funcionar sin internet y como respaldo.

**Filtro de adecuación obligatorio** (`limpieza.py`): descarta textos con temas no aptos para una niña de 12 años (violencia explícita, contenido sexual, drogas, etc.) mediante lista de palabras prohibidas y una verificación con Gemini ("¿Es este texto apropiado para una niña de 12 años? Responde solo sí/no y por qué"). Ante la duda, se descarta y se usa el banco local.

### 5.3 Longitud por nivel
- Nivel 1–2: 150–300 palabras.
- Nivel 3–4: 300–500 palabras.
- Nivel 5–6: 500–800 palabras.
- El padre puede ajustar estos rangos.

### 5.4 Generación de preguntas (`generador_preguntas.py`)
Con la **API de Gemini**, para cada lectura genera preguntas de opción múltiple (4 opciones, una correcta) que cubran los tres niveles:
- **Literal:** qué dice el texto explícitamente, significado de una palabra en contexto.
- **Inferencial:** idea principal, función de un párrafo, intención del autor, conclusión deducible.
- **Crítico:** distinguir hecho de opinión, detectar un supuesto, decir qué enunciado debilita o fortalece un argumento, relacionar con otra situación.

Prompt interno sugerido para Gemini (ajústalo):
```
Eres evaluador experto en Lectura Crítica del ICFES para estudiantes de 7.º grado en Colombia.
A partir del TEXTO, genera N preguntas de opción múltiple (4 opciones, una sola correcta) en español,
distribuidas así: {literal}, {inferencial}, {crítico}.
Cada pregunta debe incluir: enunciado, 4 opciones, índice de la correcta, el nivel (literal/inferencial/crítico)
y una EXPLICACIÓN breve de por qué la correcta lo es y por qué las otras no.
Lenguaje claro y apropiado para 12 años. Devuelve JSON válido con ese esquema.
```
**Validación:** verifica que el JSON tenga el esquema correcto, exactamente una respuesta correcta por pregunta y que las opciones no se repitan. Si falla o no hay internet, usa las preguntas del **banco local**.

### 5.5 Calificación (`calificacion.py`)
- Puntaje por pregunta y total.
- Aprobación según umbral configurable.
- Guarda el desempeño **por nivel de comprensión**, para saber en cuál está más floja (por ejemplo, bien en literal, débil en crítico).

### 5.6 Dificultad adaptativa (`dificultad.py`)
- Empieza en **Nivel 1** (textos cortos y preguntas sobre todo literales).
- Sube de nivel cuando aprueba varios tests seguidos con buen puntaje (configurable, por ejemplo 3 seguidos ≥ 85 %).
- Baja un nivel si reprueba varios seguidos.
- A mayor nivel: textos más largos, más preguntas inferenciales y críticas, y más textos discontinuos y argumentativos.

---

## 6. Enseñar primero (lo pedagógico) — `pedagogia/`

Como la niña aún no sabe estos tipos de lectura, la app **le enseña antes de exigir**. Crea **lecciones interactivas cortas** (una por tipo), que aparecen la primera vez que va a enfrentar ese tipo y quedan disponibles en un menú "Aprender":

1. **"Leer lo que dice el texto" (literal):** explica, con un ejemplo breve y resaltado en colores, cómo encontrar información explícita. Una mini-práctica de 2 preguntas con pistas.
2. **"Leer entre líneas" (inferencial):** enseña a hallar la idea principal, la intención del autor y a deducir. Ejemplo guiado paso a paso.
3. **"Leer con ojo crítico" (crítico):** explica la diferencia entre hecho, opinión y supuesto, y cómo evaluar un argumento. Ejemplo con una opinión y un hecho lado a lado.

Cada lección: lenguaje sencillo, ejemplos visuales, tono de entrenadora, y al final una práctica guiada que no cuenta como test. El **tutor** (`tutor.py`) da pistas durante las prácticas y explica cada respuesta en los tests reprobados.

Diseño instruccional: dificultad creciente, refuerzo positivo, repetición espaciada de los tipos en los que está más floja.

---

## 7. Modo padre — `ui/padre/`

Se entra desde la bandeja o desde el kiosco con un botón discreto, pidiendo la **clave del padre** (hash con argon2). Incluye:

**Configuración:**
- Minutos de recompensa por test aprobado, y umbral de aprobación.
- Tiempo de ocio inicial del día.
- Listas de apps/sitios de **ocio**, **estudio** y **neutro**.
- Horarios permitidos y bloqueados.
- Número de preguntas por test y mezcla de niveles.
- Rangos de longitud por nivel y velocidad de subida de dificultad.
- API key de Gemini (se guarda cifrada).
- Activar/desactivar el proceso vigilante.

**Estadísticas:**
- Tests hechos, aprobados y reprobados; porcentaje de acierto por nivel de comprensión (literal/inferencial/crítico) y por tipo de texto.
- Evolución del nivel en el tiempo (gráfica).
- Tiempo leído vs. tiempo jugado por día y por semana.
- Racha de días y lecturas favoritas.
- Exportar a CSV o PDF.

**Acciones:**
- Liberar el equipo ahora (cierra el kiosco).
- Regalar o quitar minutos.
- Reiniciar progreso.

---

## 8. Refuerzo con el control parental de Windows (clave para que no la evada)

En `MANUAL_PADRE.md`, incluye una guía paso a paso para que el padre configure **Microsoft Family Safety** de modo que el ocio quede bloqueado a nivel de sistema por defecto, y así cerrar la app no le devuelva el juego:
- Crear/convertir la cuenta de la niña en **cuenta infantil** del grupo Family.
- Poner **límites de tiempo de pantalla** y **límites por app** (Roblox, navegador) bajos o en cero por defecto.
- Explicar que, cuando "Lee y Juega" otorga minutos, el padre aprueba el tiempo extra desde la app Family Safety de su celular (o, si Microsoft lo permite vía su flujo, de forma asistida).
- Dejar claro el reparto: **Family Safety** impide el ocio a nivel de sistema; **"Lee y Juega"** es la vía amable y educativa para ganarse ese tiempo. Juntos, cerrar la app no sirve de nada.

No programes nada que evada o manipule Family Safety: solo documenta cómo usarlo junto con la app.

---

## 9. Datos y estadísticas (`datos/`)
Modelo SQLite con, al menos:
- `configuracion`
- `sesiones_lectura` (fecha, tipo de texto, nivel, fuente, duración)
- `tests` (preguntas, respuestas, puntaje, aprobado, niveles evaluados)
- `tiempo` (minutos ganados y gastados por día)
- `progreso_nivel` (historial de nivel)
Todo local. Respaldo automático del archivo SQLite que el padre pueda exportar.

---

## 10. Interfaz
- Tema claro, colores cálidos y amigables, tipografía grande y legible.
- Animaciones suaves de recompensa al aprobar (confeti, racha, subir de nivel).
- Botones grandes, lenguaje cercano ("¡Vamos a leer para jugar!", "¡Lo lograste!").
- Accesible: buen contraste, opción de aumentar el tamaño del texto.
- Nada de recargar la pantalla; una idea por pantalla.

---

## 11. Fases de construcción (en orden, con criterio de aceptación)

1. **Base:** proyecto, configuración, SQLite con los modelos, modo padre con clave. → Se entra al modo padre y se guarda configuración.
2. **Banco offline + lectura y test:** cargar una lectura local, mostrarla, generar el test desde el banco, calificar. → Una lectura completa de principio a fin sin internet.
3. **Ventana kiosco + banco de tiempo + monitor:** detectar ocio, descontar tiempo, mostrar el kiosco a pantalla completa siempre encima, liberar al aprobar. → Al acabarse el tiempo jugando Roblox, aparece el kiosco; al aprobar, se cierra y suma minutos.
4. **Lecturas de internet:** Vikidia/Wikipedia/Wikisource con limpieza y filtro de adecuación. → Trae y limpia textos apropiados de 7.º grado.
5. **Preguntas con Gemini:** generación, validación y respaldo offline. → Tests generados correctos; si no hay red, usa el banco.
6. **Lecciones y tutor:** las 3 lecciones interactivas y las explicaciones. → La primera vez de cada tipo, enseña antes de evaluar.
7. **Dificultad adaptativa + estadísticas completas:** subir/bajar de nivel y panel de estadísticas con gráficas. → El nivel cambia según el desempeño; el padre ve el progreso.
8. **Arranque con la sesión + vigilante opcional + instalador:** inicio automático, vigilante configurable, PyInstaller + Inno Setup. → Instalador funcional; arranca con Windows.
9. **Documentación:** `MANUAL_PADRE.md` (incluye la guía de Family Safety de la sección 8) y `PROGRESO.md`.

Al terminar cada fase: pruebas en verde y commit.

---

## 12. Reglas y límites (cúmplelas)
- **No** interceptes ni bloquees Ctrl+Alt+Supr, el Administrador de tareas ni teclas del sistema.
- **No** ocultes la app del sistema ni intentes hacerla indetectable o inmune al antivirus.
- La app debe ser **desinstalable** por el padre y por un administrador del equipo, siempre.
- El kiosco solo se libera aprobando el test o con la clave del padre.
- Todo el contenido debe ser **apropiado para una niña de 12 años**; ante la duda, descartar.
- Nada de recopilar datos de la niña hacia internet: las estadísticas son **locales**.
- La API de Gemini solo se usa para generar/validar preguntas y verificar adecuación de textos; su key va cifrada.

Entrega el código completo, comentado en español, con pruebas, instrucciones de instalación y los dos documentos de `docs/`.

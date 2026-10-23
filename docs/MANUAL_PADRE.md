# Manual del Padre — "Lee y Juega"

Bienvenido a **Lee y Juega**, la aplicación pedagógica diseñada para que tu hija de 12 años (7.º grado en Colombia) desarrolle las competencias lectoras exigidas por la prueba de **Lectura Crítica del ICFES**, transformando el tiempo de ocio digital en un hábito constructivo y motivador.

---

## 1. Filosofía de la Aplicación

- **No al castigo, sí al mérito:** La niña no es privada de jugar de manera autoritaria; se le enseña que el tiempo recreativo se gana mediante el esfuerzo intelectual y la lectura.
- **Enseñar antes de exigir:** Antes de ser evaluada, la aplicación le enseña con lecciones guiadas e interactivas los tres niveles de comprensión lectora (Literal, Inferencial y Crítico).
- **Tono de entrenador:** Cuando comete errores, un tutor pedagógico le explica con empatía por qué la respuesta correcta lo es y cómo deducirla en su próximo intento.

---

## 2. Acceso y Uso del Modo Padre

### ¿Cómo ingresar?
Puedes acceder al panel de administración en cualquier momento de dos formas:
1. Desde el **icono de la bandeja del sistema** (junto al reloj de Windows): haz clic derecho y selecciona **🔐 Modo Padre**.
2. Desde la **pantalla de bloqueo**: haz clic en el botón discreto **🔐 Modo Padre** ubicado en la esquina superior derecha.

### Clave de Seguridad (Argon2)
- En el primer inicio, el sistema te solicitará crear una contraseña segura.
- Esta clave se almacena utilizando el algoritmo criptográfico **Argon2**, garantizando que nadie pueda descifrarla ni modificar la configuración sin tu autorización.

### Pestañas del Panel de Control

#### ⚙️ Configuración
- **Recompensa por test aprobado:** Minutos de juego otorgados al aprobar (por defecto, 60 minutos).
- **Umbral de aprobación:** Porcentaje mínimo de aciertos para ganar tiempo (por defecto, 70%).
- **Tiempo de ocio inicial:** Minutos libres al arrancar el día (por defecto 0, obligando a leer para empezar a jugar).
- **Listas de Ocio y Estudio:**
  - *Ocio (descuenta tiempo y activa bloqueo):* `RobloxPlayerBeta.exe`, `Minecraft.Windows.exe`, YouTube, TikTok, Instagram, Twitch, Netflix, etc.
  - *Estudio (nunca bloquea ni descuenta tiempo):* Classroom, Word, Excel, Wikipedia, Khan Academy, Duolingo, Canva, etc.
  - *Música permitida:* Spotify o YouTube Music no descuentan tiempo si la ventana principal es educativa o neutra.
- **Horarios permitidos:** Franjas donde no se permite jugar (por ejemplo, después de las 9:00 p. m. o durante la jornada escolar).
- **Clave API de Gemini:** Si deseas que la inteligencia artificial genere lecturas y preguntas frescas y adaptadas en tiempo real, puedes colocar tu API key gratuita de Google Gemini. **La clave se guarda cifrada con DPAPI de Windows**, de modo que ningún usuario ni programa externo pueda verla en texto plano. Si no tienes o no deseas usar API key, la app funciona al 100% de manera autónoma con su banco offline de más de 40 lecturas curadas.
- **Proceso Vigilante:** Mantiene un servicio transparente en segundo plano que, en caso de que la aplicación sea cerrada por error, la vuelve a abrir automáticamente.

#### 📊 Estadísticas y Progreso
- Total de lecturas y evaluaciones realizadas.
- Tasa de aprobación porcentual.
- Desglose por dimensiones del ICFES: porcentaje de dominio en nivel **Literal**, **Inferencial** y **Crítico**.
- Gráfica semanal con **tiempo leído vs. tiempo jugado**.
- Racha de días consecutivos practicando.
- Botón para **exportar todo el historial a CSV** para seguimiento escolar.

#### ⚡ Acciones y Control Inmediato
- **Liberar equipo ahora:** Cierra inmediatamente la pantalla de bloqueo si el padre o un adulto necesita usar el computador.
- **Regalar / Retirar tiempo:** Añade o descuenta minutos con un clic (+30 min, +60 min, -30 min).
- **Copia de seguridad:** Exporta una copia completa de la base de datos SQLite para resguardar las estadísticas.

---

## 3. Refuerzo con el Control Parental de Windows (Microsoft Family Safety)

### Explicación Honesta sobre la Ventana Kiosco
La ventana de bloqueo de **Lee y Juega** es una aplicación a pantalla completa, sin bordes y siempre al frente (`WindowStaysOnTopHint`), que bloquea Alt+F4 y no permite interactuar con juegos mientras el tiempo esté en cero.

Sin embargo, por diseño ético y seguridad del sistema operativo, **la aplicación NO manipula controladores del teclado ni bloquea `Ctrl+Alt+Supr` ni el Administrador de tareas de Windows**. Un adolescente hábil podría intentar finalizar el proceso desde el Administrador de tareas si tuviera privilegios de administrador.

Por esta razón, la estrategia recomendada por expertos en seguridad familiar es **complementar "Lee y Juega" con Microsoft Family Safety**.

### Guía Paso a Paso de Configuración:

1. **Crear una cuenta infantil en Windows:**
   - Ve a **Inicio > Configuración > Cuentas > Familia y otros usuarios**.
   - Asegúrate de que la cuenta de tu hija sea una **Cuenta Estándar** (sin permisos de Administrador) vinculada al grupo familiar de Microsoft.
   - Tu cuenta como padre debe ser la única **Cuenta Administrador** del computador.

2. **Establecer límites de tiempo de pantalla base:**
   - Abre la aplicación **Microsoft Family Safety** en tu teléfono o en [family.microsoft.com](https://family.microsoft.com).
   - Ve a la cuenta de tu hija y configura el **Límite de tiempo de pantalla de Windows** o los límites individuales de aplicaciones como **Roblox** o navegadores en **0 horas** o en un límite muy bajo por defecto.

3. **El reparto de funciones perfecto:**
   - **Microsoft Family Safety** actúa como el cerrojo a nivel de núcleo del sistema: impide que la niña use juegos si no hay autorización, incluso si intentara cerrar procesos.
   - **Lee y Juega** actúa como el tutor educativo y la vía amable: le da la oportunidad autónoma de ganarse ese tiempo leyendo y comprendiendo textos reales del ICFES.
   - Cuando la niña aprueba un test en "Lee y Juega", la aplicación le otorga su tiempo y tú puedes autorizar los minutos correspondientes con un toque desde la app de tu celular si así lo requieres. Juntos, intentar cerrar la app no le permite evadir el límite.

---

## 4. Desinstalación y Mantenimiento

La aplicación respeta los estándares del sistema y puede ser desinstalada en cualquier momento por el padre o administrador:
1. Abre el **Panel de Control de Windows > Programas y características** (o Configuración > Aplicaciones instaladas).
2. Selecciona **Lee y Juega** y haz clic en **Desinstalar**.
3. El desinstalador eliminará los archivos del programa, accesos directos y configuraciones de inicio automático.

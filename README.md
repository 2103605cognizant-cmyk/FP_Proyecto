Árbol de Directorios del Proyecto
Plaintext
la_esfinge_cli/
├── audio/                  # Carpeta de recursos multimedia (.ogg) para música y efectos
├── saves/                  # Carpeta generada automáticamente para las 3 ranuras (.dat)
├── modelos.py              # Capa de Datos y Entidades del dominio (POO)
├── sistemas.py             # Capa de Infraestructura (Interfaz CLI, Audio y Persistencia)
├── combate.py              # Motor lógico de enfrentamientos por turnos
├── narrativa.py            # Motor de historia ramificada y capítulos
└── main.py                 # Orquestador principal y punto de entrada de la aplicación
Descripción Detallada por Módulo y Directorio
•	modelos.py (Entidades, Inventario y Estados) Define las clases base del dominio siguiendo PEP 8 (Estado, Objeto, Entidad, Jugador y Enemigo). Gestiona la vida máxima y actual, los atributos principales (Lucha, Destreza, Percepción y Experiencia), el equipamiento de armas, el consumo de raciones y pociones, la resolución de tiradas de habilidad (2d6) y el procesamiento por turnos de estados alterados (como veneno abisal o bendiciones permanentes).
•	sistemas.py (Interfaz CLI, Audio y Persistencia) Aísla los servicios técnicos transversales en tres clases independientes:
o	GestorAudio: Controla la reproducción de música de fondo en bucle y efectos puntuales en formato .ogg mediante pygame.mixer, incluyendo control de volumen, silencio y tolerancia a fallos si no hay dispositivo de sonido.
o	GestorGuardado: Implementa la serialización binaria mediante pickle para guardar y cargar el estado completo de la partida (objeto Jugador, escena actual y marca de tiempo) en 3 ranuras independientes (partida_slot_1.dat a 3.dat).
o	InterfazCLI: Proporciona métodos estáticos de entrada/salida en consola que capturan excepciones ValueError y validan rangos numéricos para evitar cierres inesperados por errores del usuario.
•	combate.py (Motor de Combate por Turnos) Implementa la clase MotorCombate, encargada de resolver de forma automática los enfrentamientos tácticos. Calcula la iniciativa según la Destreza, evalúa tiradas de ataque y defensa, aplica multiplicadores por golpes críticos (doble 6) y pifias (doble 1), actualiza estados alterados al inicio de cada turno, permite consumir objetos curativos en mitad de la batalla y gestiona las probabilidades de huida.
•	narrativa.py (Gestor de Escenas y Capítulos) Contiene la clase GestorNarrativa, que estructura la aventura en tres capítulos y un epílogo mediante un diccionario de escenas encadenadas. Controla el flujo de decisiones del usuario, verifica el inventario y las pistas acumuladas (pistas_y_flags) para desbloquear rutas alternativas, aplica ventajas tácticas contra los jefes e instancia dinámicamente a los enemigos de cada capítulo.
•	main.py (Punto de Entrada y Orquestador Principal) Es el fichero ejecutable que integra todos los módulos anteriores. Inicializa los gestores de audio y guardado, muestra el menú principal, ejecuta el asistente interactivo de creación de personaje (reparto validado de 23 puntos de habilidad) y mantiene el bucle principal del juego permitiendo acceder en cualquier momento al inventario, al guardado en disco o al reproductor de música.
•	audio/ y saves/ (Directorios de Recursos y Datos) El directorio audio/ almacena las pistas musicales (exploracion.ogg, combate.ogg, jefe_final.ogg) y efectos sonoros (espada.ogg, victoria.ogg). El directorio saves/ se crea dinámicamente en tiempo de ejecución para alojar los archivos binarios .dat generados por pickle.

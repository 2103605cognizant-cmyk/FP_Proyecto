"""
Módulo de Sistemas Transversales (PEP 8).
Incluye:
- Interfaz de consola (CLI) con validación estricta de entrada (ValueError).
- Gestor de Audio con pygame.mixer (música .ogg y efectos de sonido).
- Gestor de Persistencia mediante pickle en 3 ranuras (.dat).
"""

import os
import pickle
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
try:
    import pygame
    PYGAME_DISPONIBLE = True
except ImportError:
    PYGAME_DISPONIBLE = False


class GestorAudio:
    """Controla la música de fondo (.ogg) y efectos de sonido en terminal."""

    def __init__(self, directorio_audio="audio"):
        self.directorio_audio = directorio_audio
        self.habilitado = False
        self.volumen = 0.5
        self.pista_actual = None

        if PYGAME_DISPONIBLE:
            try:
                pygame.mixer.init()
                self.habilitado = True
            except pygame.error:
                self.habilitado = False

    def reproducir_musica(self, archivo_ogg):
        """Reproduce en bucle una pista .ogg si existe y el audio está activo."""
        if not self.habilitado or self.pista_actual == archivo_ogg:
            return
        ruta = os.path.join(self.directorio_audio, archivo_ogg)
        if os.path.exists(ruta):
            try:
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.set_volume(self.volumen)
                pygame.mixer.music.play(-1)
                self.pista_actual = archivo_ogg
            except pygame.error:
                pass

    def reproducir_efecto(self, archivo_ogg):
        """Reproduce un efecto puntual (espada, dados, victoria)."""
        if not self.habilitado:
            return
        ruta = os.path.join(self.directorio_audio, archivo_ogg)
        if os.path.exists(ruta):
            try:
                efecto = pygame.mixer.Sound(ruta)
                efecto.set_volume(self.volumen)
                efecto.play()
            except pygame.error:
                pass

    def alternar_silencio(self):
        if not PYGAME_DISPONIBLE:
            print("[AUDIO] Pygame no está instalado en este entorno.")
            return
        if self.habilitado:
            pygame.mixer.music.pause()
            self.habilitado = False
            print("[AUDIO] Música y efectos silenciados.")
        else:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.unpause()
                self.habilitado = True
                print("[AUDIO] Audio activado.")
            except pygame.error:
                print("[AUDIO] No se detectó dispositivo de sonido.")

    def cambiar_volumen(self, nuevo_volumen):
        self.volumen = max(0.0, min(1.0, nuevo_volumen))
        if self.habilitado:
            pygame.mixer.music.set_volume(self.volumen)


class GestorGuardado:
    """Gestiona la serialización con pickle en 3 ranuras (.dat)."""

    def __init__(self, directorio_saves="saves"):
        self.directorio_saves = directorio_saves
        os.makedirs(self.directorio_saves, exist_ok=True)

    def _ruta_ranura(self, ranura):
        return os.path.join(self.directorio_saves, f"partida_slot_{ranura}.dat")

    def obtener_resumen_ranuras(self):
        resumen = {}
        for slot in (1, 2, 3):
            ruta = self._ruta_ranura(slot)
            if os.path.exists(ruta):
                try:
                    with open(ruta, "rb") as archivo:
                        datos = pickle.load(archivo)
                    jugador = datos["jugador"]
                    capitulo = datos["capitulo_nombre"]
                    resumen[slot] = (
                        f"OCUPADA -> {jugador.nombre} | PI: {jugador.vida_actual}/{jugador.vida_max} "
                        f"| Escena: {capitulo}"
                    )
                except (pickle.UnpicklingError, KeyError, EOFError):
                    resumen[slot] = "ARCHIVO CORRUPTO"
            else:
                resumen[slot] = "[VACÍA]"
        return resumen

    def guardar_partida(self, ranura, jugador, seccion_actual, capitulo_nombre):
        if ranura not in (1, 2, 3):
            return False, "Ranura no válida. Debe ser 1, 2 o 3."
        datos = {
            "jugador": jugador,
            "seccion_actual": seccion_actual,
            "capitulo_nombre": capitulo_nombre,
            "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        try:
            with open(self._ruta_ranura(ranura), "wb") as archivo:
                pickle.dump(datos, archivo)
            return True, f"Partida guardada correctamente en la Ranura {ranura}."
        except OSError as err:
            return False, f"Error de escritura en disco: {err}"

    def cargar_partida(self, ranura):
        if ranura not in (1, 2, 3):
            return None, "Ranura no válida."
        ruta = self._ruta_ranura(ranura)
        if not os.path.exists(ruta):
            return None, f"La Ranura {ranura} está vacía."
        try:
            with open(ruta, "rb") as archivo:
                datos = pickle.load(archivo)
            return datos, f"Partida cargada desde la Ranura {ranura} ({datos['fecha']})."
        except (pickle.UnpicklingError, EOFError, OSError) as err:
            return None, f"No se pudo cargar el archivo: {err}"


class InterfazCLI:
    """Utilidades de entrada y salida en consola resistentes a errores."""

    @staticmethod
    def separador(caracter="=", ancho=68):
        print(caracter * ancho)

    @staticmethod
    def pedir_entero(mensaje, minimo, maximo):
        """Evita cierres por ValueError solicitando entrada hasta que sea válida."""
        while True:
            entrada = input(mensaje).strip()
            try:
                valor = int(entrada)
                if minimo <= valor <= maximo:
                    return valor
                print(f"[!] Por favor, introduce un número entre {minimo} y {maximo}.")
            except ValueError:
                print("[!] Entrada inválida. Debes introducir un número entero.")

    @staticmethod
    def pedir_opcion(opciones_validas, mensaje="\n--> Elige una opción: "):
        """Valida elecciones de menú."""
        opciones_norm = [str(op).lower() for op in opciones_validas]
        while True:
            entrada = input(mensaje).strip().lower()
            if entrada in opciones_norm:
                return entrada
            print(f"[!] Opción incorrecta. Valores permitidos: {', '.join(opciones_validas)}")

    @staticmethod
    def pausa(segundos=0.8):
        time.sleep(segundos)
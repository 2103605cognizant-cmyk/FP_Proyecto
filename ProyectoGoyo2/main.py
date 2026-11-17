"""
Punto de Entrada Principal - La Esfinge (AD&D Aventura Juego 14).
Arquitectura Modular en Python 3.12 (PEP 8).
"""

import sys
from modelos import Jugador
from narrativa import GestorNarrativa
from sistemas import GestorAudio, GestorGuardado, InterfazCLI

5

def asistente_creacion_personaje():
    """Asistente interactivo con validación estricta para configurar a Sir Theobold."""
    InterfazCLI.separador("=")
    print(" CREACIÓN DE PERSONAJE: SIR THEOBOLD BARBARROJA")
    InterfazCLI.separador("=")
    print("Reparte 23 puntos entre Lucha, Destreza y Percepción (mínimo 6 en cada una).")

    while True:
        lucha = InterfazCLI.pedir_entero("  Puntos de LUCHA (6-11): ", 6, 11)
        destreza = InterfazCLI.pedir_entero("  Puntos de DESTREZA (6-11): ", 6, 11)
        percepcion = InterfazCLI.pedir_entero("  Puntos de PERCEPCIÓN (6-11): ", 6, 11)

        if lucha + destreza + percepcion == 23:
            break
        print(
            f"[!] La suma actual es {lucha + destreza + percepcion}. "
            "Debe sumar exactamente 23 puntos."
        )

    jugador = Jugador(vida_max=32, lucha=lucha, destreza=destreza, percepcion=percepcion, experiencia=3)
    print(f"\n[PERSONAJE LISTO] {jugador.nombre} creado con {jugador.vida_max} PI.")
    return jugador


def menu_inventario(jugador):
    """Permite consultar ficha, equipar armas o usar pociones/raciones."""
    while True:
        InterfazCLI.separador("-")
        print(
            f"FICHA: {jugador.nombre} | PI: {jugador.vida_actual}/{jugador.vida_max} "
            f"| Exp: {jugador.experiencia}"
        )
        print(
            f"Stats -> Lucha: {jugador.obtener_lucha_efectiva()} | Destreza: {jugador.destreza} "
            f"| Percepción: {jugador.percepcion}"
        )
        print(f"Arma equipada: {jugador.arma_equipada.nombre}")
        print("\nInventario:")
        for idx, item in enumerate(jugador.inventario, start=1):
            print(f"  {idx}) {item}")

        print("\nOpciones: [Número] Usar/Equipar objeto | [0] Volver")
        eleccion = InterfazCLI.pedir_entero("--> Selección: ", 0, len(jugador.inventario))
        if eleccion == 0:
            break
        _, mensaje = jugador.usar_consumible(eleccion - 1)
        print(f"  {mensaje}")


def menu_guardado_carga(guardado, modo, jugador=None, seccion_actual=1, capitulo=""):
    """Gestiona las 3 ranuras de persistencia (.dat) con pickle."""
    InterfazCLI.separador("-")
    print(f" SISTEMA DE PERSISTENCIA ({modo.upper()}) - 3 RANURAS (.dat)")
    InterfazCLI.separador("-")
    resumen = guardado.obtener_resumen_ranuras()
    for slot, info in resumen.items():
        print(f"  Ranura {slot}: {info}")
    print("  0) Cancelar y volver")

    slot = InterfazCLI.pedir_entero("\n--> Elige ranura (0-3): ", 0, 3)
    if slot == 0:
        return None

    if modo == "guardar":
        _, msg = guardado.guardar_partida(slot, jugador, seccion_actual, capitulo)
        print(f"[DISCO] {msg}")
        return None

    datos, msg = guardado.cargar_partida(slot)
    print(f"[DISCO] {msg}")
    return datos


def menu_audio(audio):
    """Control de música de fondo (.ogg) y volumen."""
    InterfazCLI.separador("-")
    print(" REPRODUCTOR DE MÚSICA Y SONIDO (pygame.mixer)")
    InterfazCLI.separador("-")
    print("  1) Activar / Silenciar música y efectos")
    print("  2) Subir volumen (+20%)")
    print("  3) Bajar volumen (-20%)")
    print("  0) Volver")

    op = InterfazCLI.pedir_opcion(["1", "2", "3", "0"])
    if op == "1":
        audio.alternar_silencio()
    elif op == "2":
        audio.cambiar_volumen(audio.volumen + 0.2)
        print(f"[AUDIO] Volumen al {int(audio.volumen * 100)}%")
    elif op == "3":
        audio.cambiar_volumen(audio.volumen - 0.2)
        print(f"[AUDIO] Volumen al {int(audio.volumen * 100)}%")


def main():
    audio = GestorAudio()
    guardado = GestorGuardado()
    audio.reproducir_musica("menu_principal.ogg")

    InterfazCLI.separador("*")
    print("   ADVANCED DUNGEONS & DRAGONS: LA ESFINGE (CLI EDITION)")
    InterfazCLI.separador("*")
    print("  1) Nueva Partida")
    print("  2) Cargar Partida (Ranuras 1-3)")
    print("  3) Salir")

    inicio = InterfazCLI.pedir_opcion(["1", "2", "3"])
    if inicio == "3":
        sys.exit(0)

    jugador = None
    seccion_actual = 1

    if inicio == "2":
        datos_cargados = menu_guardado_carga(guardado, modo="cargar")
        if datos_cargados:
            jugador = datos_cargados["jugador"]
            seccion_actual = datos_cargados["seccion_actual"]
        else:
            print("Iniciando nueva partida por defecto...")

    if jugador is None:
        jugador = asistente_creacion_personaje()

    narrativa = GestorNarrativa(jugador, audio)

    # Bucle principal de juego
    while seccion_actual > 0:
        capitulo_actual = narrativa.obtener_nombre_capitulo(seccion_actual)
        InterfazCLI.separador("=")
        print(
            f"[PI: {jugador.vida_actual}/{jugador.vida_max} | Exp: {jugador.experiencia} "
            f"| {capitulo_actual}]"
        )
        print("Comandos: [ENTER] Continuar | [I] Inventario/Pociones | [G] Guardar | [M] Música | [S] Salir")
        cmd = input("--> ").strip().lower()

        if cmd == "i":
            menu_inventario(jugador)
            continue
        if cmd == "g":
            menu_guardado_carga(guardado, "guardar", jugador, seccion_actual, capitulo_actual)
            continue
        if cmd == "m":
            menu_audio(audio)
            continue
        if cmd == "s":
            print("Saliendo del juego. ¡Hasta la próxima aventura!")
            sys.exit(0)

        seccion_actual = narrativa.ejecutar_escena(seccion_actual)

    if seccion_actual == -1:
        InterfazCLI.separador("!")
        print(" HAS CAÍDO EN COMBATE. FIN DE LA AVENTURA.")
        InterfazCLI.separador("!")


if __name__ == "__main__":
    main()
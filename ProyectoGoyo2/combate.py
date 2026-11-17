"""
Motor de Combate por Turnos (PEP 8).
Resuelve iniciativa, tiradas de ataque, golpes críticos, uso de pociones y huidas.
"""

import random
from sistemas import InterfazCLI


class MotorCombate:
    """Gestiona los enfrentamientos tácticos por turnos entre Jugador y Enemigo."""

    def __init__(self, jugador, enemigo, audio):
        self.jugador = jugador
        self.enemigo = enemigo
        self.audio = audio
        self.turno = 1

    def ejecutar_combate(self):
        """
        Ejecuta el bucle de combate hasta que uno muera o el jugador huya.
        Devuelve: 'victoria', 'derrota' o 'huida'.
        """
        self.audio.reproducir_musica("combate.ogg")
        InterfazCLI.separador("!")
        print(f"¡COMBATE INICIADO CONTRA: {self.enemigo.nombre.upper()}!")
        print(f"Descripción: {self.enemigo.descripcion}")
        InterfazCLI.separador("!")

        while self.jugador.esta_vivo() and self.enemigo.esta_vivo():
            print(f"\n--- TURNO {self.turno} ---")
            print(
                f"{self.jugador.nombre}: {self.jugador.vida_actual}/{self.jugador.vida_max} PI "
                f"| Arma: {self.jugador.arma_equipada.nombre}"
            )
            print(
                f"{self.enemigo.nombre}: {self.enemigo.vida_actual}/{self.enemigo.vida_max} PI"
            )

            # Procesar estados alterados (ej. veneno)
            for msg in self.jugador.procesar_estados_turno():
                print(msg)
            for msg in self.enemigo.procesar_estados_turno():
                print(msg)

            if not self.jugador.esta_vivo():
                return "derrota"
            if not self.enemigo.esta_vivo():
                return "victoria"

            # Menú de acción del jugador en el turno
            print("\nAcciones disponibles:")
            print("  1) Atacar con arma")
            print("  2) Usar poción o ración del inventario")
            print("  3) Intentar huir del combate")

            accion = InterfazCLI.pedir_opcion(["1", "2", "3"])

            if accion == "2":
                self._turno_inventario()
                if self.enemigo.esta_vivo():
                    self._ataque_enemigo()
            elif accion == "3":
                if self._intentar_huir():
                    return "huida"
                self._ataque_enemigo()
            else:
                self._resolver_intercambio_golpes()

            self.turno += 1
            InterfazCLI.pausa(0.7)

        if self.jugador.esta_vivo():
            self.audio.reproducir_efecto("victoria.ogg")
            print(f"\n[VICTORIA] ¡Has derrotado a {self.enemigo.nombre}!")
            self.jugador.experiencia += 1
            print("[PROGRESO] Ganas +1 Punto de Experiencia.")
            return "victoria"

        self.audio.reproducir_efecto("derrota.ogg")
        return "derrota"

    def _resolver_intercambio_golpes(self):
        """Determina quién golpea primero según Destreza y resuelve ambos ataques."""
        if self.jugador.destreza >= self.enemigo.destreza:
            self._ataque_jugador()
            if self.enemigo.esta_vivo():
                self._ataque_enemigo()
        else:
            print(f"{self.enemigo.nombre} es más rápido y ataca primero.")
            self._ataque_enemigo()
            if self.jugador.esta_vivo():
                self._ataque_jugador()

    def _ataque_jugador(self):
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        tirada = d1 + d2
        ataque_jugador = tirada + self.jugador.obtener_lucha_efectiva()
        defensa_enemigo = 7 + self.enemigo.lucha

        self.audio.reproducir_efecto("espada.ogg")

        if tirada == 2:
            print(f"  [PIFIA] Sacas doble 1. Tu golpe falla por completo.")
            return

        if tirada == 12 or ataque_jugador >= defensa_enemigo:
            dano = self.jugador.dano_base + self.jugador.arma_equipada.valor_efecto
            if tirada == 12:
                dano *= 2
                print(
                    f"  [¡GOLPE CRÍTICO!] Doble 6 ({ataque_jugador} vs {defensa_enemigo}). "
                    f"Infliges {dano} PI de daño devastador a {self.enemigo.nombre}."
                )
            else:
                print(
                    f"  [IMPACTO] Tirada {ataque_jugador} vs {defensa_enemigo}. "
                    f"Infliges {dano} PI de daño a {self.enemigo.nombre}."
                )
            self.enemigo.recibir_dano(dano)
        else:
            print(
                f"  [FALLO] Tu ataque ({ataque_jugador}) es bloqueado por {self.enemigo.nombre} ({defensa_enemigo})."
            )

    def _ataque_enemigo(self):
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        tirada = d1 + d2
        ataque_enemigo = tirada + self.enemigo.obtener_lucha_efectiva()
        defensa_jugador = 7 + self.jugador.destreza

        if tirada == 12 or ataque_enemigo >= defensa_jugador:
            dano = self.enemigo.dano_base
            if tirada == 12:
                dano = int(dano * 1.5)
                print(
                    f"  [¡CRÍTICO ENEMIGO!] {self.enemigo.nombre} encuentra un hueco en tu guardia "
                    f"y te inflige {dano} PI de daño."
                )
            else:
                print(
                    f"  [HERIDA] {self.enemigo.nombre} te golpea ({ataque_enemigo} vs {defensa_jugador}) "
                    f"causándote {dano} PI de daño."
                )
            self.jugador.recibir_dano(dano)
        else:
            print(
                f"  [ESQUIVA] Logras desviar el ataque de {self.enemigo.nombre} ({ataque_enemigo} vs {defensa_jugador})."
            )

    def _turno_inventario(self):
        consumibles = [
            (idx, obj)
            for idx, obj in enumerate(self.jugador.inventario)
            if obj.categoria in ("pocion", "racion") and obj.usos > 0
        ]
        if not consumibles:
            print("  [!] No tienes pociones ni raciones disponibles. Pierdes la oportunidad.")
            return

        print("  Selecciona qué consumir:")
        for i, (_, obj) in enumerate(consumibles, start=1):
            print(f"    {i}) {obj}")
        eleccion = InterfazCLI.pedir_entero("  Número: ", 1, len(consumibles))
        indice_real = consumibles[eleccion - 1][0]
        _, mensaje = self.jugador.usar_consumible(indice_real)
        print(f"  {mensaje}")

    def _intentar_huir(self):
        if not self.enemigo.permite_huida:
            print(f"  [!] ¡No hay escapatoria posible frente a {self.enemigo.nombre}!")
            return False

        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        if d1 + d2 + self.jugador.destreza >= 10 + self.enemigo.destreza:
            print(f"  [HUIDA] Consigues retirarte tácticamente del combate contra {self.enemigo.nombre}.")
            return True
        print("  [!] El enemigo te corta el paso y no logras huir.")
        return False
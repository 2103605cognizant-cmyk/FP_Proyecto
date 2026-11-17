"""
Gestor de Escenas y Narrativa por Capítulos (PEP 8).
Controla la historia ramificada de 'La Esfinge' y las transiciones de estado.
"""

from combate import MotorCombate
from modelos import Enemigo, Estado, Objeto
from sistemas import InterfazCLI


class GestorNarrativa:
    """Administra las escenas del librojuego organizadas por capítulos."""

    def __init__(self, jugador, audio):
        self.jugador = jugador
        self.audio = audio
        self.escenas = {
            1: ("Capítulo I: El Desastre de Lighthall", self.escena_1_inicio),
            2: ("Capítulo I: Las Cuevas del Acantilado", self.escena_2_acantilado),
            3: ("Capítulo I: El Acertijo de las Esfinges", self.escena_3_acertijo),
            4: ("Capítulo I: Las Colinas del Dragón", self.escena_4_colinas_dragon),
            5: ("Capítulo I: El Lago Encantado", self.escena_5_lago_encantado),
            6: ("Capítulo II: Trann, la Isla Flotante", self.escena_6_trann),
            7: ("Capítulo II: El Templo y el Diario de Saybrook", self.escena_7_investigacion),
            8: ("Capítulo II: Las Mazmorras de los Ogros", self.escena_8_mazmorras),
            9: ("Capítulo III: La Cima de la Tormenta (Durhan)", self.escena_9_batalla_final),
            10: ("Epílogo: El Regreso de Lighthall", self.escena_10_victoria),
        }

    def obtener_nombre_capitulo(self, id_escena):
        datos = self.escenas.get(id_escena)
        return datos[0] if datos else "Desconocido"

    def ejecutar_escena(self, id_escena):
        """Ejecuta la función de la escena indicada y devuelve el ID de la siguiente."""
        if id_escena not in self.escenas:
            return 0
        titulo, funcion = self.escenas[id_escena]
        InterfazCLI.separador("-")
        print(f" {titulo.upper()}")
        InterfazCLI.separador("-")
        return funcion()

    # --------------------------------------------------------------------------
    # CAPÍTULO I: LA BÚSQUEDA DE LAS MONEDAS MÁGICAS
    # --------------------------------------------------------------------------

    def escena_1_inicio(self):
        self.audio.reproducir_musica("exploracion.ogg")
        print("Un estruendo rasga el cielo de Lighthall. Una esfera de luz envuelve tu reino y")
        print("lo hace desaparecer ante tus ojos. Del firmamento cae un meteoro con la proyección")
        print("del Mago Supremo Warrick: 'El brujo Durhan ha secuestrado nuestras ciudades en la")
        print("dimensión de Trann. Reúne las monedas de Oro, Plata y Platino para detenerlo.'")
        print("\nCon la Moneda de Cobre en tu mano y Theona a tu lado, decides tu próximo destino:")
        print("  1) Viajar a las Cuevas del Acantilado (Moneda de Oro).")
        print("  2) Explorar las Colinas del Dragón (Moneda de Plata).")
        print("  3) Investigar el Lago Encantado (Moneda de Platino).")
        print("  4) Activar el portal de la Moneda de Cobre hacia Trann.")

        op = InterfazCLI.pedir_opcion(["1", "2", "3", "4"])
        return {"1": 2, "2": 4, "3": 5, "4": 6}[op]

    def escena_2_acantilado(self):
        self.audio.reproducir_musica("misterio.ogg")
        if "moneda_oro" in self.jugador.pistas_y_flags:
            print("Las esfinges ya te entregaron su tesoro. Regresas al cruce principal.")
            return 1

        print("Ante una caverna se alzan Demóstenes y Neria, dos majestuosas esfinges aladas.")
        print("Demóstenes habla con voz profunda: 'La Moneda de Oro será tuya si superas nuestro")
        print("acertijo lógico... o si nos derrotas en combate.'")
        print("\n  1) Aceptar el desafío del acertijo.")
        print("  2) Desenvainar tu espada y atacar a las esfinges.")
        print("  3) Regresar al cruce de caminos.")

        op = InterfazCLI.pedir_opcion(["1", "2", "3"])
        if op == "1":
            return 3
        if op == "2":
            esfinges = Enemigo(
                "Pareja de Esfinges", vida_max=22, lucha=9, destreza=9, dano_base=6,
                descripcion="Leones alados de garras afiladas y sabiduría ancestral."
            )
            resultado = MotorCombate(self.jugador, esfinges, self.audio).ejecutar_combate()
            if resultado == "derrota":
                return -1
            if resultado == "victoria":
                self._otorgar_moneda_oro()
            return 1
        return 1

    def escena_3_acertijo(self):
        print("Demóstenes explica: 'Uno de nosotros siempre dice la verdad y el otro siempre miente.'")
        print("  - Demóstenes dice: 'La esfinge que tiene la moneda siempre dice la verdad.'")
        print("  - Neria dice: 'Mentira. La esfinge que tiene la moneda siempre miente.'")
        print("\n¿Quién custodia realmente la Moneda de Oro?")
        print("  1) Demóstenes")
        print("  2) Neria")

        op = InterfazCLI.pedir_opcion(["1", "2"])
        if op == "1":
            print("\n[ÉXITO] Has resuelto la paradoja lógica. Demóstenes inclina la cabeza y te entrega")
            print("la reliquia dorada.")
            self.jugador.experiencia += 2
            self._otorgar_moneda_oro()
            return 1

        print("\n[FALLO] Tu respuesta es errónea. Las esfinges rugen y se lanzan al ataque.")
        esfinges = Enemigo(
            "Pareja de Esfinges", vida_max=22, lucha=9, destreza=9, dano_base=6,
            descripcion="Guardianas enfurecidas del acantilado."
        )
        resultado = MotorCombate(self.jugador, esfinges, self.audio).ejecutar_combate()
        if resultado == "derrota":
            return -1
        if resultado == "victoria":
            self._otorgar_moneda_oro()
        return 1

    def _otorgar_moneda_oro(self):
        self.jugador.pistas_y_flags.add("moneda_oro")
        self.jugador.agregar_objeto(
            Objeto("Moneda de Oro (Jacaine)", "llave", "Permite metamorfosis y abre sellos.", usos=-1)
        )
        print("[OBJETO OBTENIDO] Moneda de Oro de Jacaine.")

    def escena_4_colinas_dragon(self):
        self.audio.reproducir_musica("tension.ogg")
        if "moneda_plata" in self.jugador.pistas_y_flags:
            print("La guarida de Dominagon está en silencio. Vuelves al cruce.")
            return 1

        print("En las colinas calcinadas hallas a Granito, un gigante herido tras enfrentar a")
        print("Dominagon el Azul, guardián de la Moneda de Plata.")
        print("\n  1) Entregar una Poción Curativa a Granito para que luche contigo.")
        print("  2) Entrar solo en la caverna del dragón.")
        print("  3) Volver al cruce.")

        op = InterfazCLI.pedir_opcion(["1", "2", "3"])
        if op == "3":
            return 1

        vida_dragon = 28
        if op == "1":
            pocion = self.jugador.tiene_item("Poción Curativa")
            if pocion and pocion.usos > 0:
                pocion.usos -= 1
                print("\nGranito bebe la poción, recupera sus fuerzas y carga contra el dragón")
                print("debilitándolo antes de caer agotado (-10 PI al dragón).")
                vida_dragon = 18
                self.jugador.experiencia += 1
            else:
                print("\n[!] No te quedan pociones curativas. Entras solo a la cueva.")

        dragon = Enemigo(
            "Dominagon el Azul", vida_max=vida_dragon, lucha=10, destreza=8, dano_base=7,
            descripcion="Dragón adulto de escamas azul cobalto y aliento eléctrico."
        )
        resultado = MotorCombate(self.jugador, dragon, self.audio).ejecutar_combate()
        if resultado == "derrota":
            return -1
        if resultado == "victoria":
            self.jugador.pistas_y_flags.add("moneda_plata")
            self.jugador.agregar_objeto(
                Objeto("Moneda de Plata (Saybrook)", "llave", "Invoca ilusiones arcanas.", usos=-1)
            )
            self.jugador.agregar_objeto(
                Objeto("Espada Matadragones", "arma", "Hoja rúnica (+4 daño).", usos=-1, valor_efecto=4)
            )
            print("[BOTÍN] Obtienes la Moneda de Plata y la Espada Matadragones (+4 daño).")
        return 1

    def escena_5_lago_encantado(self):
        self.audio.reproducir_musica("misterio.ogg")
        if "moneda_platino" in self.jugador.pistas_y_flags:
            print("Las aguas del lago están en calma. Regresas al cruce.")
            return 1

        print("En el fondo del Lago Encantado brilla la Moneda de Platino, custodiada por un")
        print("enjambre de Peces Diabólicos venenosos.")
        print("\n  1) Bucear con sigilo para robar la moneda (Prueba de Destreza 14+).")
        print("  2) Sumergirte espada en mano para combatirlos.")
        print("  3) Regresar al cruce.")

        op = InterfazCLI.pedir_opcion(["1", "2", "3"])
        if op == "3":
            return 1

        if op == "1":
            gasto = InterfazCLI.pedir_entero(
                f"¿Cuánta Experiencia gastar en la tirada? (0-{self.jugador.experiencia}): ",
                0,
                self.jugador.experiencia,
            )
            exito, detalle = self.jugador.tirar_habilidad("destreza", 14, gasto)
            print(f"  {detalle}")
            if exito:
                print("[ÉXITO] Tomas la Moneda de Platino sin alertar a las criaturas.")
                self._otorgar_moneda_platino()
                return 1
            print("[FALLO] ¡Has golpeado el coral y los peces diabólicos te rodean!")

        peces = Enemigo(
            "Enjambre de Peces Diabólicos", vida_max=18, lucha=8, destreza=10, dano_base=5,
            descripcion="Depredadores abisales con aguijones venenosos."
        )
        # Aplican estado de veneno al iniciar combate
        self.jugador.agregar_estado(
            Estado("Veneno Abisal", "Pierdes 2 PI por turno durante 2 turnos.", turnos_restantes=2, dano_por_turno=2)
        )
        print("[ESTADO] ¡Has sido envenenado por las aguas tóxicas!")

        resultado = MotorCombate(self.jugador, peces, self.audio).ejecutar_combate()
        if resultado == "derrota":
            return -1
        if resultado == "victoria":
            self._otorgar_moneda_platino()
        return 1

    def _otorgar_moneda_platino(self):
        self.jugador.pistas_y_flags.add("moneda_platino")
        self.jugador.agregar_objeto(
            Objeto("Moneda de Platino (Dyan)", "llave", "Domina voluntades y purifica altares.", usos=-1)
        )
        print("[OBJETO OBTENIDO] Moneda de Platino de Dyan.")

    # --------------------------------------------------------------------------
    # CAPÍTULO II: LA DIMENSIÓN DE TRANN
    # --------------------------------------------------------------------------

    def escena_6_trann(self):
        self.audio.reproducir_musica("trann.ogg")
        print("La Moneda de Cobre abre un portal dimensional. Apareces en Trann, una isla flotante")
        print("bajo un sol interior donde yacen las ruinas de Solius.")
        print("\n  1) Explorar el Templo de Dyan y la Casa-Dragón de Saybrook.")
        print("  2) Descender a las mazmorras custodiadas por ogros.")
        print("  3) Subir directamente a la cima de la tormenta para enfrentar a Durhan.")

        op = InterfazCLI.pedir_opcion(["1", "2", "3"])
        return {"1": 7, "2": 8, "3": 9}[op]

    def escena_7_investigacion(self):
        print("En el estudio de Saybrook descubres un diario secreto con una pista vital:")
        print("'Durhan porta el Cinturón Negro de Orcus, que lo hace invulnerable al fuego.")
        print("Solo puede ser vencido con estos Anillos de Protección Ignífuga o liberando a")
        print("los cuatro Magos Supremos encadenados en el sótano.'")

        if "pista_cinturon" not in self.jugador.pistas_y_flags:
            self.jugador.pistas_y_flags.add("pista_cinturon")
            self.jugador.agregar_objeto(
                Objeto("Anillos de Protección Ignífuga", "reliquia", "Inmunidad al fuego de Orcus.", usos=-1)
            )
            self.jugador.agregar_objeto(
                Objeto("Poción Curativa Suprema", "pocion", "Restaura 25 PI.", usos=1, valor_efecto=25)
            )
            print("[PISTA Y EQUIPO] Obtienes los Anillos de Protección y una Poción Suprema.")

        if self.jugador.tiene_item("Moneda de Platino"):
            print("\nEn el altar de Dyan, tu Moneda de Platino brilla y te bendice (+2 Lucha).")
            self.jugador.agregar_estado(
                Estado("Bendición de Dyan", "+2 permanente en Lucha.", turnos_restantes=-1, mod_lucha=2)
            )

        print("\n¿Hacia dónde continúas?")
        print("  1) Bajar a las mazmorras para rescatar a los Magos Supremos.")
        print("  2) Ir directo a la batalla final contra Durhan.")
        return 8 if InterfazCLI.pedir_opcion(["1", "2"]) == "1" else 9

    def escena_8_mazmorras(self):
        print("Tres enormes ogros custodian a los Magos Supremos bajo un Ojo de Espectador.")
        ogros = Enemigo(
            "Guardia de Ogros", vida_max=24, lucha=9, destreza=7, dano_base=6,
            descripcion="Brutos acorazados con garrotes de hierro."
        )
        resultado = MotorCombate(self.jugador, ogros, self.audio).ejecutar_combate()
        if resultado == "derrota":
            return -1
        if resultado == "victoria":
            self.jugador.pistas_y_flags.add("magos_liberados")
            self.jugador.curar(self.jugador.vida_max)
            print("\n[ALIADOS] ¡Los cuatro Magos Supremos son libres! Curan todas tus heridas")
            print("y debilitarán el escudo mágico de Durhan en el combate final.")
        return 9

    # --------------------------------------------------------------------------
    # CAPÍTULO III: BATALLA FINAL Y EPÍLOGO
    # --------------------------------------------------------------------------

    def escena_9_batalla_final(self):
        self.audio.reproducir_musica("jefe_final.ogg")
        print("En la cúspide de la torre, Durhan el Conquistador flota envuelto en llamas negras")
        print("ceñido por el Cinturón Negro de Orcus.")

        vida_durhan = 36
        dano_durhan = 9

        if "pista_cinturon" in self.jugador.pistas_y_flags:
            print("[VENTAJA] Tus Anillos de Protección Ignífuga anulan el aura de fuego de Durhan.")
            dano_durhan -= 3
        if "magos_liberados" in self.jugador.pistas_y_flags:
            print("[VENTAJA] Los Magos Supremos canalizan un rayo arcano que debilita a Durhan (-10 PI).")
            vida_durhan -= 10

        durhan = Enemigo(
            "Durhan el Conquistador", vida_max=vida_durhan, lucha=11, destreza=10, dano_base=dano_durhan,
            descripcion="Archimago corrupto portador del Cinturón Negro de Orcus.",
            permite_huida=False
        )
        resultado = MotorCombate(self.jugador, durhan, self.audio).ejecutar_combate()
        if resultado == "victoria":
            return 10
        return -1

    def escena_10_victoria(self):
        self.audio.reproducir_musica("victoria_final.ogg")
        InterfazCLI.separador("*")
        print(" ¡VICTORIA TOTAL! EL CINTURÓN NEGRO DE ORCUS SE DESINTEGRA.")
        InterfazCLI.separador("*")
        print("Con Durhan derrotado, los Magos Supremos invocan el gran hechizo de restauración.")
        print("Solius vuelve a brillar en Trann y las murallas, plazas y habitantes de Lighthall")
        print("reaparecen intactos en tu mundo. Junto a Theona, la paz regresa al reino.")
        return 0
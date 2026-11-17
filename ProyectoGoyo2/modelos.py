"""
Módulo de Entidades y Modelos de Datos (PEP 8).
Define las clases Objeto, Estado, Personaje, Jugador y Enemigo.
"""

import random


class Estado:
    """Representa un estado temporal o permanente que afecta a una entidad."""

    def __init__(self, nombre, descripcion, turnos_restantes=-1, mod_lucha=0, dano_por_turno=0):
        self.nombre = nombre
        self.descripcion = descripcion
        self.turnos_restantes = turnos_restantes  # -1 = permanente hasta curarse
        self.mod_lucha = mod_lucha
        self.dano_por_turno = dano_por_turno


class Objeto:
    """Representa armas, raciones, pociones y reliquias mágicas."""

    def __init__(self, nombre, categoria, descripcion, usos=1, valor_efecto=0, stat_afectado=None):
        self.nombre = nombre
        self.categoria = categoria  # 'arma', 'pocion', 'racion', 'reliquia', 'llave'
        self.descripcion = descripcion
        self.usos = usos            # -1 para equipamiento permanente
        self.valor_efecto = valor_efecto
        self.stat_afectado = stat_afectado

    def __str__(self):
        usos_info = "Equipado" if self.usos == -1 else f"Usos: {self.usos}"
        return f"{self.nombre} [{self.categoria.upper()}] ({usos_info}) - {self.descripcion}"


class Entidad:
    """Clase base para cualquier ser vivo o enemigo en combate."""

    def __init__(self, nombre, vida_max, lucha, destreza, dano_base):
        self.nombre = nombre
        self.vida_max = vida_max
        self.vida_actual = vida_max
        self.lucha = lucha
        self.destreza = destreza
        self.dano_base = dano_base
        self.estados = []

    def esta_vivo(self):
        return self.vida_actual > 0

    def recibir_dano(self, cantidad):
        self.vida_actual = max(0, self.vida_actual - cantidad)
        return cantidad

    def curar(self, cantidad):
        vida_previa = self.vida_actual
        self.vida_actual = min(self.vida_max, self.vida_actual + cantidad)
        return self.vida_actual - vida_previa

    def agregar_estado(self, estado):
        self.estados.append(estado)

    def procesar_estados_turno(self):
        """Aplica efectos de estado al inicio/fin de cada turno y reduce duración."""
        mensajes = []
        estados_activos = []
        for est in self.estados:
            if est.dano_por_turno > 0:
                self.recibir_dano(est.dano_por_turno)
                mensajes.append(
                    f"[ESTADO] {self.nombre} sufre {est.dano_por_turno} de daño por {est.nombre}."
                )
            if est.turnos_restantes > 0:
                est.turnos_restantes -= 1
            if est.turnos_restantes != 0:
                estados_activos.append(est)
            else:
                mensajes.append(f"[ESTADO] El efecto '{est.nombre}' sobre {self.nombre} ha terminado.")
        self.estados = estados_activos
        return mensajes

    def obtener_lucha_efectiva(self):
        bono_estados = sum(est.mod_lucha for est in self.estados)
        return self.lucha + bono_estados


class Jugador(Entidad):
    """Representa al protagonista: Sir Theobold Barbarroja."""

    def __init__(self, vida_max=32, lucha=8, destreza=8, percepcion=7, experiencia=3):
        super().__init__("Sir Theobold Barbarroja", vida_max, lucha, destreza, dano_base=6)
        self.percepcion = percepcion
        self.experiencia = experiencia
        self.arma_equipada = Objeto(
            "Espada Ancha de Lighthall", "arma", "Acero templado (+2 daño).", usos=-1, valor_efecto=2
        )
        self.inventario = [
            self.arma_equipada,
            Objeto("Poción Curativa", "pocion", "Restaura 15 Puntos de Impacto.", usos=2, valor_efecto=15),
            Objeto("Ración de Viaje", "racion", "Recupera 6 PI y energía al descansar.", usos=3, valor_efecto=6),
            Objeto("Moneda de Cobre (Warrick)", "llave", "Abre portales hacia Trann.", usos=-1),
        ]
        self.companeros = ["Theona"]
        self.pistas_y_flags = set()

    def agregar_objeto(self, nuevo_obj):
        for obj in self.inventario:
            if obj.nombre == nuevo_obj.nombre and obj.usos != -1:
                obj.usos += nuevo_obj.usos
                return
        self.inventario.append(nuevo_obj)
        if nuevo_obj.stat_afectado == "lucha":
            self.lucha += nuevo_obj.valor_efecto
        elif nuevo_obj.stat_afectado == "destreza":
            self.destreza += nuevo_obj.valor_efecto
        elif nuevo_obj.stat_afectado == "percepcion":
            self.percepcion += nuevo_obj.valor_efecto

    def tiene_item(self, nombre_parcial):
        for obj in self.inventario:
            if nombre_parcial.lower() in obj.nombre.lower() and (obj.usos > 0 or obj.usos == -1):
                return obj
        return None

    def usar_consumible(self, indice):
        """Usa una poción o ración por su índice en el inventario."""
        if 0 <= indice < len(self.inventario):
            obj = self.inventario[indice]
            if obj.categoria in ("pocion", "racion") and obj.usos > 0:
                obj.usos -= 1
                curado = self.curar(obj.valor_efecto)
                if obj.categoria == "pocion":
                    self.estados = [e for e in self.estados if e.dano_por_turno == 0]
                return True, f"Usas {obj.nombre} y recuperas {curado} Puntos de Impacto."
            if obj.categoria == "arma":
                self.arma_equipada = obj
                return True, f"Te equipas con {obj.nombre}."
        return False, "Ese objeto no se puede consumir o equipar ahora."

    def tirar_habilidad(self, stat_nombre, dificultad, gasto_exp=0):
        """Resuelve una tirada de 2d6 + Habilidad + Experiencia gastada."""
        valor_base = getattr(self, stat_nombre.lower())
        if stat_nombre.lower() == "lucha":
            valor_base = self.obtener_lucha_efectiva()

        gasto_exp = min(gasto_exp, self.experiencia)
        self.experiencia -= gasto_exp

        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        total = d1 + d2 + valor_base + gasto_exp
        exito = total >= dificultad
        detalle = (
            f"Dados [{d1}+{d2}={d1 + d2}] + {stat_nombre.capitalize()} ({valor_base}) "
            f"+ Exp ({gasto_exp}) = {total} (Objetivo: {dificultad}+)"
        )
        return exito, detalle


class Enemigo(Entidad):
    """Representa a los adversarios instanciables del librojuego."""

    def __init__(self, nombre, vida_max, lucha, destreza, dano_base, descripcion, permite_huida=True):
        super().__init__(nombre, vida_max, lucha, destreza, dano_base)
        self.descripcion = descripcion
        self.permite_huida = permite_huida
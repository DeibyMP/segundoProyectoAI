import customtkinter
import random
from tkinter import *
from PIL import *
from dataclasses import dataclass
from collections import deque

tamanho_tablero = 8
puntos = [-10, -5, -4, -3, -1, 1, 3, 4, 5, 10]

@dataclass
class EstadoJuego:
    tablero: list
    posicion_cab_blanco: tuple
    posicion_cab_negro: tuple
    destruida: set
    puntos_cab_blanco: int
    puntos_cab_negro: int
    turno: str

    def copy(self):
        return EstadoJuego(
            tablero=[fila[:] for fila in self.tablero],
            posicion_cab_blanco=tuple(self.posicion_cab_blanco),
            posicion_cab_negro=tuple(self.posicion_cab_negro),
            destruida=set(self.destruida),
            puntos_cab_blanco=self.puntos_cab_blanco,
            puntos_cab_negro=self.puntos_cab_negro,
            turno=self.turno
        )

    def obtener_mov_caballo(self, pos):
        (r, c) = pos
        moves = [(r+2, c+1), (r+2, c-1),
                 (r-2, c+1), (r-2, c-1),
                 (r+1, c+2), (r+1, c-2),
                 (r-1, c+2), (r-1, c-2)]
        valid = []
        for rr, cc in moves:
            if 0 <= rr < 8 and 0 <= cc < 8 and (rr, cc) not in self.destruida:
                if self.turno == 'blanco' and (rr, cc) != self.posicion_cab_negro:
                    valid.append((rr, cc))
                if self.turno == 'negro' and (rr, cc) != self.posicion_cab_blanco:
                    valid.append((rr, cc))
        return valid

    def tiene_movimientos(self, player):
        if player == 'blanco':
            return len(self.obtener_mov_caballo(self.posicion_cab_blanco)) > 0
        else:
            actual = self.turno
            self.turno = player
            res = len(self.obtener_mov_caballo(self.posicion_cab_negro)) > 0
            self.turno = actual
            return res

    def hacer_movimiento(self, player, dest):
        st = self.copy()
        if player == 'blanco':
            prev = st.posicion_cab_blanco
            # destruimos la celda previa
            st.destruida.add(prev)
            # si la celda de llegada tiene valor lo sumamos
            val = st.tablero[dest[0]][dest[1]]
            if val is not None:
                st.puntos_cab_blanco += val
            # quitamos el valor de la celda
            st.tablero[dest[0]][dest[1]] = None
            # movemos el caballo
            st.posicion_cab_blanco = dest
            # destruimos la celda donde quedo
            st.destruida.add(dest)
            # cambiamos el turno
            st.turno = 'negro'
        else:
            prev = st.posicion_cab_negro
            st.destruida.add(prev)
            val = st.tablero[dest[0]][dest[1]]
            if val is not None:
                st.puntos_cab_negro += val
            st.tablero[dest[0]][dest[1]] = None
            st.posicion_cab_negro = dest
            st.destruida.add(dest)
            st.turno = 'blanco'
        return st

class SmartHorsesApp(customtkinter.CTk):

    def __init__(self):
        super().__init__()
        self.geometry("1000x800")
        customtkinter.set_appearance_mode("light")
        self.title("Smart Horses")
        self.interfaz_dificultad()

        # estado de la interfaz
        self.caballo_seleccionado = None
        self.resaltar_celdas = []
        self.celdas_destruidas = set()
        self.puntos_negro = 0
        self.puntos_blanco = 0

        # profundidad por defecto
        self.profundidad_limite = 0

        self.caballo_blanco_img = None
        self.caballo_negro_img = None

    def interfaz_dificultad(self):
        self.limpiar_interfaz()
        # Botones de dificultad
        self.texto_dificultad = customtkinter.CTkLabel(self, text="SELECCIONE LA DIFICULTDAD", text_color="black", font=("Times New Roman", 50, "bold"))
        self.texto_dificultad.place(relx=0.5, rely=0.35, anchor="center")

        self.btn_principiante = customtkinter.CTkButton(self, text="Principiante", fg_color="grey", text_color="white", font=("Times New Roman", 40, "bold"),
                                                        height=50, width=250, corner_radius=10, border_width=1.2, border_color="black",
                                                        command=lambda: self.comenzar_juego('principiante'))
        self.btn_principiante.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_amateur = customtkinter.CTkButton(self, text="Amateur", fg_color="grey", text_color="white", font=("Times New Roman", 40, "bold"),
                                                   height=50, width=250, corner_radius=10, border_width=1.2, border_color="black",
                                                   command=lambda: self.comenzar_juego('amateur'))
        self.btn_amateur.place(relx=0.5, rely=0.58, anchor="center")

        self.btn_experto = customtkinter.CTkButton(self, text="Experto", fg_color="grey", text_color="white", font=("Times New Roman", 40, "bold"),
                                                   height=50, width=250, corner_radius=10, border_width=1.2, border_color="black",
                                                   command=lambda: self.comenzar_juego('experto'))
        self.btn_experto.place(relx=0.5, rely=0.66, anchor="center")

    def comenzar_juego(self, dificultad):
        if dificultad == 'principiante':
            self.profundidad_limite = 2
        elif dificultad == 'amateur':
            self.profundidad_limite = 4
        else:
            self.profundidad_limite = 6

        # limpiamos la Interfaz anterior
        self.limpiar_interfaz()

        self.label_puntos_negro = customtkinter.CTkLabel(self, text="Puntos Caballo Negro: 0", text_color="black", font=("Arial", 25, "bold"))
        self.label_puntos_negro.place(relx=0.15, rely=0.05)

        self.label_puntos_blanco = customtkinter.CTkLabel(self, text="Puntos Caballo Blanco: 0", text_color="black", font=("Arial", 25, "bold"))
        self.label_puntos_blanco.place(relx=0.55, rely=0.05)

        self.canvas = Canvas(self, width=640, height=640, bg="white")
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_reiniciar = customtkinter.CTkButton(self, text="Reiniciar", fg_color="grey", text_color="white", font=("Times New Roman", 40, "bold"),
                                                   height=50, width=200, corner_radius=10, border_width=1.2, border_color="black",
                                                   command=self.reiniciar_juego)
        self.btn_reiniciar.place(relx=0.84, rely=0.94, anchor="center")

        self.crear_tablero()

        # estado del juego inicial
        self.celdas_destruidas = set()
        self.puntos_negro = 0
        self.puntos_blanco = 0

        # creamos el estado inicial de EstadoJuego
        self.estado_juego = EstadoJuego(
            tablero=[fila[:] for fila in self.tablero],
            posicion_cab_blanco=self.posicion_caballo_blanco,
            posicion_cab_negro=self.posicion_caballo_negro,
            destruida=set(self.celdas_destruidas),
            puntos_cab_blanco=self.puntos_blanco,
            puntos_cab_negro=self.puntos_negro,
            turno='blanco'
        )

        # Registramos los clicks del usuario
        self.canvas.bind("<Button-1>", self.click_tablero)

        self.after(300, self.movimientos_maquina)

    def crear_tablero(self):
        self.tablero = [[None for _ in range(tamanho_tablero)] for _ in range(tamanho_tablero)]
        tamanho_celdas = 80

        # Dibujamos el tablero
        for fila in range(tamanho_tablero):
            for columna in range(tamanho_tablero):
                color = "#989898" if (fila + columna) % 2 else "#ffffff"
                self.canvas.create_rectangle(
                    columna * tamanho_celdas, fila * tamanho_celdas,
                    (columna + 1) * tamanho_celdas, (fila + 1) * tamanho_celdas,
                    fill=color,
                    tags=f"celda_{fila}_{columna}"
                )

        # colocamos los numeros y caballos en posiciones aleatorias
        posiciones = [(fila, columna) for fila in range(8) for columna in range(8)]
        random.shuffle(posiciones)

        posiciones_numeros = posiciones[:10]
        posiciones_caballos = posiciones[10:12]

        valores = puntos[:]
        random.shuffle(valores)

        for (fila, columna), val in zip(posiciones_numeros, valores):
            x = columna * tamanho_celdas + 40
            y = fila * tamanho_celdas + 40
            self.canvas.create_text(x, y, text=str(val), font=("Times New Roman", 30, "bold"), fill="black", tags=f"numero_{fila}_{columna}")
            self.tablero[fila][columna] = val

        # Cargamos las imagenes de los caballos
        img_caballo_blanco = Image.open("imagenes/caballoBlanco.png").resize((70, 70))
        img_caballo_negro = Image.open("imagenes/caballoNegro.png").resize((90, 90))

        self.caballo_blanco_img = ImageTk.PhotoImage(img_caballo_blanco)
        self.caballo_negro_img = ImageTk.PhotoImage(img_caballo_negro)

        # Guardamos las posiciones de los caballos
        self.posicion_caballo_blanco = posiciones_caballos[0]
        self.posicion_caballo_negro = posiciones_caballos[1]

        # Dibujamos los caballos
        self.caballo_blanco = self.canvas.create_image(
            self.posicion_caballo_blanco[1] * 80 + 40,
            self.posicion_caballo_blanco[0] * 80 + 40,
            image=self.caballo_blanco_img,
            tags="caballo_blanco"
        )

        self.caballo_negro = self.canvas.create_image(
            self.posicion_caballo_negro[1] * 80 + 40,
            self.posicion_caballo_negro[0] * 80 + 40,
            image=self.caballo_negro_img,
            tags="caballo_negro"
        )

    def click_tablero(self, event):
        # Verificamos si el juego ya termino
        if not hasattr(self, 'estado_juego'):
            return
            
        columna = event.x // 80
        fila = event.y // 80
        
        #Cuando el usuario selecciona el caballo
        if self.es_caballo_negro(fila, columna):
            self.caballo_seleccionado = "negro"
            self.mostrar_movimientos_posibles()
            return

        # Movemos el caballo a la celda escogida
        for (r, c) in self.resaltar_celdas:
            if r == fila and c == columna:
                self.mover_caballo_negro(r, c)
                # Verificamos estado despues del movimiento
                self.verificar_y_continuar_juego()
                return

    def es_caballo_negro(self, fila, columna):
        return (fila, columna) == self.posicion_caballo_negro

    def mostrar_movimientos_posibles(self):
        self.limpiar_resaltados()

        r, c = self.posicion_caballo_negro
        movimientos = [
            (r+2, c+1), (r+2, c-1),
            (r-2, c+1), (r-2, c-1),
            (r+1, c+2), (r+1, c-2),
            (r-1, c+2), (r-1, c-2),
        ]

        validos = []
        for rr, cc in movimientos:
            if (rr, cc) == self.posicion_caballo_blanco:
                continue
            if 0 <= rr < 8 and 0 <= cc < 8:
                if (rr, cc) not in self.celdas_destruidas:
                    validos.append((rr, cc))

        # Resaltamos
        for (rr, cc) in validos:
            self.canvas.create_rectangle(
                cc * 80, rr * 80, cc * 80 + 80, rr * 80 + 80,
                outline="red", width=4, tags="highlight"
            )

        self.resaltar_celdas = validos

    def mover_caballo_negro(self, r, c):
        # Destruimos la celda anterior
        fila_anterior, columna_anterior = self.posicion_caballo_negro
        self.destruir_celda(fila_anterior, columna_anterior)

        valor = self.tablero[r][c]
        if valor is not None:
            self.puntos_negro += valor
            self.label_puntos_negro.configure(text=f"Puntos Caballo Negro: {self.puntos_negro}")

        self.tablero[r][c] = None

        # Movemos imagen el caballo
        self.canvas.coords(self.caballo_negro, c * 80 + 40, r * 80 + 40)

        # Actualizamos la posicion del caballo
        self.posicion_caballo_negro = (r, c)

        # Destruimos celda
        self.destruir_celda(r, c)
        self.limpiar_resaltados()

        self.estado_juego.posicion_cab_negro = self.posicion_caballo_negro
        self.estado_juego.tablero = [fila[:] for fila in self.tablero]
        self.estado_juego.destruida = set(self.celdas_destruidas)
        self.estado_juego.puntos_cab_negro = self.puntos_negro
        self.estado_juego.turno = 'blanco'

    def destruir_celda(self, r, c):
        self.celdas_destruidas.add((r, c))
        # Pintamos la celda destruida
        self.canvas.itemconfig(f"celda_{r}_{c}", fill="#ff873d")
        # Borramos el numero de la celda (si existe)
        self.canvas.delete(f"numero_{r}_{c}")

    def limpiar_resaltados(self):
        self.canvas.delete("highlight")
        self.resaltar_celdas = []

    def limpiar_interfaz(self):
        for widget in self.winfo_children():
            widget.destroy()
    
    def reiniciar_juego(self):

        if hasattr(self, 'after_id'):
            self.after_cancel(self.after_id)
        
        if hasattr(self, 'canvas'):
            self.canvas.unbind("<Button-1>")
        
        # Resetear variables de estado
        self.caballo_seleccionado = None
        self.resaltar_celdas = []
        self.celdas_destruidas = set()
        self.puntos_negro = 0
        self.puntos_blanco = 0
        self.profundidad_limite = 0
    
        if hasattr(self, 'estado_juego'):
            del self.estado_juego
        
        self.interfaz_dificultad()

    def verificar_y_continuar_juego(self):
        st = self.estado_juego
        
        # Obtenemos movimientos posibles para ambos jugadores
        movimientos_blanco = st.obtener_mov_caballo(st.posicion_cab_blanco)
        st.turno = 'negro'
        movimientos_negro = st.obtener_mov_caballo(st.posicion_cab_negro)
        st.turno = 'blanco'
        
        # Ambos sin movimientos -> Fin del juego
        if not movimientos_blanco and not movimientos_negro:
            self.finalizar_juego()
            return
        
        # El Caballo Negro no tiene movimientos pero el Caballo blanco si tiene
        if not movimientos_negro and movimientos_blanco:
            # Penalizamos al Caballo negro
            st.puntos_cab_negro -= 4
            self.puntos_negro = st.puntos_cab_negro
            self.label_puntos_negro.configure(text=f"Puntos Caballo Negro: {self.puntos_negro}")
            self.estado_juego = st
            
            # La maquina sigue jugando
            self.after(500, self.movimientos_maquina)
            return
        
        # Ambos Caballos tienen movimientos o solo negro tiene -> turno de la maquina
        self.after(300, self.movimientos_maquina)


    def movimientos_maquina(self):
        st = self.estado_juego

        # comprobamos movimientos de ambos jugadores
        movimientos_blanco = st.obtener_mov_caballo(st.posicion_cab_blanco)
        st.turno = 'negro'
        movimientos_negro = st.obtener_mov_caballo(st.posicion_cab_negro)
        st.turno = 'blanco'

        # Ambos sin movimientos -> terminamos el juego
        if not movimientos_blanco and not movimientos_negro:
            self.finalizar_juego()
            return

        # El CaballoBlanco sin movimientos pero el Caballo Negro si tiene
        if not movimientos_blanco and movimientos_negro:
            st.puntos_cab_blanco -= 4
            self.puntos_blanco = st.puntos_cab_blanco
            self.label_puntos_blanco.configure(text=f"Puntos Caballo Blanco: {self.puntos_blanco}")
            st.turno = 'negro'
            self.estado_juego = st
            return
        
        #El Caballo Blanco tiene movimientos -> llamamos a el algoritrhmo miniMax para que la maquina juegue
        mejor_valor, mejor_movimiento = self.eleccion_miniMax(st, self.profundidad_limite)
        if mejor_movimiento is None:
            self.finalizar_juego()
            return

        # aplicamos el movimiento elegido por la maquina
        nuevo_estado_movimiento = st.hacer_movimiento('blanco', mejor_movimiento)

        # actualizamos la interfaz
        prev_r, prev_c = st.posicion_cab_blanco
        self.destruir_celda(prev_r, prev_c)

        val = self.tablero[mejor_movimiento[0]][mejor_movimiento[1]]
        if val is not None:
            self.puntos_blanco += val
            self.label_puntos_blanco.configure(text=f"Puntos Caballo Blanco: {self.puntos_blanco}")

        self.tablero[mejor_movimiento[0]][mejor_movimiento[1]] = None
        self.canvas.coords(self.caballo_blanco, mejor_movimiento[1] * 80 + 40, mejor_movimiento[0] * 80 + 40)
        self.posicion_caballo_blanco = mejor_movimiento
        self.destruir_celda(mejor_movimiento[0], mejor_movimiento[1])

        # actualizamos el estado_juego
        self.estado_juego = nuevo_estado_movimiento
        self.puntos_blanco = nuevo_estado_movimiento.puntos_cab_blanco
        self.puntos_negro = nuevo_estado_movimiento.puntos_cab_negro
        self.label_puntos_blanco.configure(text=f"Puntos Caballo Blanco: {self.puntos_blanco}")
        self.label_puntos_negro.configure(text=f"Puntos Caballo Negro: {self.puntos_negro}")

        # Despues de mover el caballo blanco, verificamos si el caballo negro puede jugar
        # Si el caballo negro no tiene movimientos, la maquina debe seguir jugando
        movimientos_cab_blanco = nuevo_estado_movimiento.obtener_mov_caballo(nuevo_estado_movimiento.posicion_cab_blanco)
        nuevo_estado_movimiento.turno = 'negro'
        movimientos_cab_negro = nuevo_estado_movimiento.obtener_mov_caballo(nuevo_estado_movimiento.posicion_cab_negro)
        nuevo_estado_movimiento.turno = 'blanco'
        
        # Si ambos caballos no tienen movimientos -> terminamos el juego
        if not movimientos_cab_blanco and not movimientos_cab_negro:
            self.finalizar_juego()
            return
        
        # Si el caballo negro no tiene movimientos pero el caballo blanco si -> penalizamos y sigue jugando
        if not movimientos_cab_negro and movimientos_cab_blanco:
            nuevo_estado_movimiento.puntos_cab_negro -= 4
            self.puntos_negro = nuevo_estado_movimiento.puntos_cab_negro
            self.label_puntos_negro.configure(text=f"Puntos Caballo Negro: {self.puntos_negro}")
            self.estado_juego = nuevo_estado_movimiento
            self.after(500, self.movimientos_maquina)
            return

    def eleccion_miniMax(self, estado: EstadoJuego, profundidad_limit):
        moves = estado.obtener_mov_caballo(estado.posicion_cab_blanco)
        if not moves:
            return self.funcion_heuristica(estado), None

        mejor_valor = float('-inf')
        mejor_movimientos = []
        alpha = float('-inf')
        beta = float('inf')

        for mv in moves:
            child = estado.hacer_movimiento('blanco', mv)
            val = self.algorithmo_miniMax(child, profundidad_limit - 1, alpha, beta, maximizing=False)
            if val > mejor_valor:
                mejor_valor = val
                mejor_movimientos = [mv]
            elif val == mejor_valor:
                mejor_movimientos.append(mv)
            alpha = max(alpha, mejor_valor)
            if alpha >= beta:
                break

        chosen = random.choice(mejor_movimientos) if mejor_movimientos else None
        return mejor_valor, chosen

    def algorithmo_miniMax(self, estado: EstadoJuego, profundidad, alpha, beta, maximizing):
        el_blanco_tiene = estado.obtener_mov_caballo(estado.posicion_cab_blanco)
        cur_turno = estado.turno
        estado.turno = 'negro'
        el_negro_tiene = estado.obtener_mov_caballo(estado.posicion_cab_negro)
        estado.turno = cur_turno

        if (not el_blanco_tiene) and (not el_negro_tiene):
            return self.funcion_heuristica(estado)

        if profundidad == 0:
            return self.funcion_heuristica(estado)

        if estado.turno == 'blanco':
            moves = estado.obtener_mov_caballo(estado.posicion_cab_blanco)
            if not moves:
                if el_negro_tiene:
                    st2 = estado.copy()
                    st2.puntos_cab_blanco -= 4
                    st2.turno = 'negro'
                    return self.algorithmo_miniMax(st2, profundidad - 1, alpha, beta, maximizing=False)
                else:
                    return self.funcion_heuristica(estado)
            value = float('-inf')
            for mv in moves:
                child = estado.hacer_movimiento('blanco', mv)
                val = self.algorithmo_miniMax(child, profundidad - 1, alpha, beta, maximizing=False)
                value = max(value, val)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            moves = estado.obtener_mov_caballo(estado.posicion_cab_negro)
            if not moves:
                if el_blanco_tiene:
                    st2 = estado.copy()
                    st2.puntos_cab_negro -= 4
                    st2.turno = 'blanco'
                    return self.algorithmo_miniMax(st2, profundidad - 1, alpha, beta, maximizing=True)
                else:
                    return self.funcion_heuristica(estado)
            value = float('inf')
            for mv in moves:
                child = estado.hacer_movimiento('negro', mv)
                val = self.algorithmo_miniMax(child, profundidad - 1, alpha, beta, maximizing=True)
                value = min(value, val)
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    def funcion_heuristica(self, estado: EstadoJuego):

        #medimos y obtenemos la diferencia de puntos entre el cab blanco y el negro
        diferencia_puntos = estado.puntos_cab_blanco - estado.puntos_cab_negro

        #Calculamos la movilidad de cada caballo 
        #para mirar quien tiene mas opciones o posibilidades
        movimientos_blanco = len(estado.obtener_mov_caballo(estado.posicion_cab_blanco))
        cur_turno = estado.turno
        estado.turno = 'negro'
        movimientos_negro = len(estado.obtener_mov_caballo(estado.posicion_cab_negro))
        estado.turno = cur_turno
        movilidad = movimientos_blanco - movimientos_negro

        potencial_blanco = 0
        potencial_negro = 0

        puntos_restantes = []

        for r in range(8):
            for c in range(8):
                v = estado.tablero[r][c]
                if v is not None and (r, c) not in estado.destruida:
                    puntos_restantes.append(((r, c), v))

        def distancia_minima_caballo(start, target, destruida):
            if start == target:
                return 0
            q = deque()
            visitada = set()
            q.append((start, 0))
            visitada.add(start)
            while q:
                (r, c), d = q.popleft()
                for nr, nc in [(r+2, c+1), (r+2, c-1), (r-2, c+1), (r-2, c-1),
                               (r+1, c+2), (r+1, c-2), (r-1, c+2), (r-1, c-2)]:
                    if 0 <= nr < 8 and 0 <= nc < 8 and (nr, nc) not in destruida and (nr, nc) not in visitada:
                        if (nr, nc) == target:
                            return d + 1
                        visitada.add((nr, nc))
                        q.append(((nr, nc), d + 1))
            return 999
        
        #Calculamos que tan cerca estan los caballos de los puntos restantes
        for (pos, val) in puntos_restantes:
            distancia_blanco = distancia_minima_caballo(estado.posicion_cab_blanco, pos, estado.destruida)
            distancia_negro = distancia_minima_caballo(estado.posicion_cab_negro, pos, estado.destruida)
            if distancia_blanco < distancia_negro:
                potencial_blanco += val * (1 / (1 + distancia_blanco))
            elif distancia_negro < distancia_blanco:
                potencial_negro += val * (1 / (1 + distancia_negro))
            else:
                potencial_blanco += 0.5 * val * (1 / (1 + distancia_blanco)) if distancia_blanco < 999 else 0
                potencial_negro += 0.5 * val * (1 / (1 + distancia_negro)) if distancia_negro < 999 else 0

        potencial = potencial_blanco - potencial_negro
        #Con valor_heuristica lo que calculamos y conseguimos es un valor final
        #con el que la maquina podra ussarlo para encontrar el mejor movimiento
        #posible, usando los datos de la diferencia_puntos, potencial(que tan cerca -
        # o lejos esta un caballo de un puntos positivo) y movilidad(que tantos -
        # posibles movimientos tienen los caballos).
        valor_heuristica = (1.0 * diferencia_puntos) + (0.6 * potencial) + (0.3 * movilidad)

        return valor_heuristica


    def finalizar_juego(self):
        self.canvas.unbind("<Button-1>")
        
        w = self.estado_juego.puntos_cab_blanco
        b = self.estado_juego.puntos_cab_negro
        self.puntos_blanco = w
        self.puntos_negro = b
        self.label_puntos_blanco.configure(text=f"Puntos Caballo Blanco: {w}")
        self.label_puntos_negro.configure(text=f"Puntos Caballo Negro: {b}")

        if w > b:
            texto = f"¡El Caballo Blanco Gana! {w} vs {b}"
        elif b > w:
            texto = f"¡El Caballo Negro Gana! {b} vs {w}"
        else:
            texto = f"Empate {w} - {b}"

        self.resultado_label = customtkinter.CTkLabel(self, text=texto, text_color="black", font=("Arial", 30, "bold"))
        self.resultado_label.place(relx=0.5, rely=0.92, anchor="center")

# Ejecutar la aplicacion
if __name__ == "__main__":
    app = SmartHorsesApp()
    app.mainloop()
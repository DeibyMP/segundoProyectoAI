from tkinter import*
from PIL import Image, ImageTk
import customtkinter
import random

tamanho_tablero = 8
puntos = [-10, -5, -4, -3, -1, 1, 3, 4, 5, 10]

class SmartHorsesApp(customtkinter.CTk):

    def __init__(self):
        super().__init__()
        self.geometry("1000x800")
        #Establecemos el tema predeterminado de la ventana
        customtkinter.set_appearance_mode("light")
        self.title("Smart Horses")
        self.interfaz_dificultad()

        self.caballo_seleccionado = None
        self.resaltar_casillas = []
        self.celdas_destruidas = set()

        self.puntos_negro = 0
        self.puntos_blanco = 0
    
    def interfaz_dificultad(self):

        #Botones de dificultad
        self.texto_dificultad = customtkinter.CTkLabel(self, text="SELECCIONE LA DIFICULTDAD", text_color="black", font=("Times New Roman", 50, "bold"))
        self.texto_dificultad.place(relx=0.5, rely=0.35, anchor="center")

        self.btn_principiante = customtkinter.CTkButton(self, text="Principiante", fg_color="grey", text_color="white", font=("Times New Roman", 40, "bold"), height=50, width=250, corner_radius=10, border_width=1.2, border_color="black", command=self.comenzar_juego)
        self.btn_principiante.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_amateur = customtkinter.CTkButton(self, text="Amateur", fg_color="grey", text_color="white", font=("Times New Roman", 40, "bold"), height=50, width=250, corner_radius=10, border_width=1.2, border_color="black", command=self.comenzar_juego)
        self.btn_amateur.place(relx=0.5, rely=0.58, anchor="center")

        self.btn_experto = customtkinter.CTkButton(self, text="Experto", fg_color="grey", text_color="white", font=("Times New Roman", 40, "bold"), height=50, width=250, corner_radius=10, border_width=1.2, border_color="black", command=self.comenzar_juego)
        self.btn_experto.place(relx=0.5, rely=0.66, anchor="center")

    def comenzar_juego(self):
        #Funcion para mostrar el tablero
        self.limpiar_interfaz()

        self.label_puntos_negro = customtkinter.CTkLabel(self, text="Puntos Caballo Negro: 0", text_color="black", font=("Arial", 25, "bold"))
        self.label_puntos_negro.place(relx=0.15, rely=0.05)

        self.label_puntos_blanco = customtkinter.CTkLabel(self, text="Puntos Caballo Blanco: 0", text_color="black", font=("Arial", 25, "bold"))
        self.label_puntos_blanco.place(relx=0.55, rely=0.05)

        self.canvas = Canvas(self, width=640, height=640, bg="white")
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")

        self.crear_tablero()
        
        #Registramos los clicks del usuario
        self.canvas.bind("<Button-1>", self.click_tablero)

    def crear_tablero(self):
        self.board = [[None for _ in range(tamanho_tablero)] for _ in range(tamanho_tablero)]
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

        for (fila, columna), val in zip(posiciones_numeros, puntos):
            x = columna * tamanho_celdas + 40
            y = fila * tamanho_celdas + 40
            self.canvas.create_text(x, y, text=str(val), font=("Times New Roman", 30, "bold"), fill="black", tags=f"numero_{fila}_{columna}")
            self.board[fila][columna] = val

        # Cargarmos las imagenes de los caballos
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

        columna = event.x // 80
        fila = event.y // 80

        # EL usuario selecciona el caballo negro
        if self.es_caballo_negro(fila, columna):
            self.caballo_seleccionado = "negro"
            self.mostrar_movimientos_posibles()
            return

        # Mover el caballo a la celda escogida
        for (r, c) in self.resaltar_casillas:
            if r == fila and c == columna:
                self.mover_caballo_negro(r, c)
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

        self.resaltar_casillas = validos

    def mover_caballo_negro(self, r, c):

        # Destruimos la celda anterior
        fila_anterior, columna_anterior = self.posicion_caballo_negro
        self.destruir_celda(fila_anterior, columna_anterior)

        valor = self.board[r][c]
        if valor is not None:
            self.puntos_negro += valor
            self.label_puntos_negro.configure(text=f"Puntos Caballo Negro: {self.puntos_negro}")

        self.board[r][c] = None

        # Movemos imagen el caballo
        self.canvas.coords(self.caballo_negro, c * 80 + 40, r * 80 + 40)

        # Actualizamos la posicion del caballo
        self.posicion_caballo_negro = (r, c)

        # Destruimos celda
        self.destruir_celda(r, c)
        self.limpiar_resaltados()

    def destruir_celda(self, r, c):

        self.celdas_destruidas.add((r, c))

        # Pintamos la celda destruida
        self.canvas.itemconfig(f"celda_{r}_{c}", fill="#ff873d")

        # Borrarmos el numero de la celda
        self.canvas.delete(f"numero_{r}_{c}")

    def limpiar_resaltados(self):
        self.canvas.delete("highlight")
        self.resaltar_casillas = []

    def limpiar_interfaz(self):
        for widget in self.winfo_children():
            widget.destroy()

app = SmartHorsesApp()
app.mainloop()
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

        self.canvas = Canvas(self, width=640, height=640, bg="white")
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")

        self.crear_tablero()
    
    def crear_tablero(self):
        self.board = [[None for _ in range(tamanho_tablero)] for _ in range(tamanho_tablero)]
        tamanho_celdas = 80

        # Dibujar tablero
        for r in range(tamanho_tablero):
            for c in range(tamanho_tablero):
                color = "#989898" if (r + c) % 2 else "#ffffff"
                self.canvas.create_rectangle(
                    c * tamanho_celdas, r * tamanho_celdas,
                    (c + 1) * tamanho_celdas, (r + 1) * tamanho_celdas,
                    fill=color
                )

        # Colocamos los numeros y caballos en posiciones aleatorias
        posiciones = [(r, c) for r in range(8) for c in range(8)]
        random.shuffle(posiciones)

        posiciones_numeros = posiciones[:10]
        posiciones_caballos = posiciones[10:12]

        for (r, c), val in zip(posiciones_numeros, puntos):
            x = c * tamanho_celdas + 40
            y = r * tamanho_celdas + 40
            self.canvas.create_text(x, y, text=str(val), font=("Times New Roman", 30, "bold"), fill="black")
            self.board[r][c] = val

        # Cargarmos las imagenes de los caballos
        img_caballo_blanco = Image.open("imagenes/caballoBlanco.png").resize((70, 70))
        img_caballo_negro = Image.open("imagenes/caballoNegro.png").resize((90, 90))

        self.caballo_blanco_img = ImageTk.PhotoImage(img_caballo_blanco)
        self.caballo_negro_img = ImageTk.PhotoImage(img_caballo_negro)

        # Guardamos las posiciones de los caballos
        self.posicion_caballo_blanco = posiciones_caballos[0]
        self.posicion_caballo_nergo = posiciones_caballos[1]

        # Dibujamos los caballos
        self.caballo_blanco = self.canvas.create_image(
            self.posicion_caballo_blanco[1] * 80 + 40,
            self.posicion_caballo_blanco[0] * 80 + 40,
            image=self.caballo_blanco_img,
            tags="knight"
        )

        self.caballo_negro = self.canvas.create_image(
            self.posicion_caballo_nergo[1] * 80 + 40,
            self.posicion_caballo_nergo[0] * 80 + 40,
            image=self.caballo_negro_img,
            tags="knight"
        )

    def limpiar_interfaz(self):
        for widget in self.winfo_children():
            widget.destroy()

app = SmartHorsesApp()
app.mainloop()
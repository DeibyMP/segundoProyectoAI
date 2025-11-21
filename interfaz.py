from tkinter import*
import customtkinter

class SmartHorsesApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1000x800")
        #Establecemos el tema predeterminado de la ventana
        customtkinter.set_appearance_mode("light")

        self.texto_dificultad = customtkinter.CTkLabel(self, text="SELECCIONE LA DIFICULTDAD", text_color="black", font=("Times New Roman", 50, "bold"))
        self.texto_dificultad.place(relx=0.5, rely=0.35, anchor="center")

        self.btn_principiante = customtkinter.CTkButton(self, text="Principiante", fg_color="grey", text_color="white", font=("Times New Roman", 40, "bold"), height=50, width=250, corner_radius=10, border_width=1.2, border_color="black")
        self.btn_principiante.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_amateur = customtkinter.CTkButton(self, text="Amateur", fg_color="grey", text_color="white", font=("Times New Roman", 40, "bold"), height=50, width=250, corner_radius=10, border_width=1.2, border_color="black")
        self.btn_amateur.place(relx=0.5, rely=0.58, anchor="center")

        self.btn_experto = customtkinter.CTkButton(self, text="Experto", fg_color="grey", text_color="white", font=("Times New Roman", 40, "bold"), height=50, width=250, corner_radius=10, border_width=1.2, border_color="black")
        self.btn_experto.place(relx=0.5, rely=0.66, anchor="center")

app = SmartHorsesApp()
app.mainloop()
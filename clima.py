import requests
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import geocoder
import datetime
import threading
import itertools

# 🔹 API Key de OpenWeatherMap
API_KEY = "b89a019e51a3a9eebebb7191df13bcbc"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
ICON_URL = "https://openweathermap.org/img/wn/{}@2x.png"

# 🔹 Configuración de la UI
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

ventana = ctk.CTk()
ventana.title("🌎 Clima PRO")
ventana.geometry("500x700")

frame = ctk.CTkFrame(ventana, corner_radius=20, fg_color="#1E1E1E")
frame.pack(pady=20, padx=20, fill="both", expand=True)

# 🔹 Convertir fecha a día de la semana
def convertir_fecha_a_dia(fecha):
    dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    fecha_obj = datetime.datetime.strptime(fecha, "%Y-%m-%d")
    return dias[fecha_obj.weekday()]

# 🔹 Obtener ubicación automática
def obtener_ubicacion():
    g = geocoder.ip("me")
    if g.city:
        entrada_ciudad.delete(0, "end")
        entrada_ciudad.insert(0, g.city)

# 🔹 Lista de favoritos
favoritos = []

def agregar_favorito():
    ciudad = entrada_ciudad.get()
    if ciudad and ciudad not in favoritos:
        favoritos.append(ciudad)
        lista_favoritos.insert("end", ciudad)

# 🔹 Obtener el clima
def obtener_clima():
    ciudad = entrada_ciudad.get()
    
    if not ciudad:
        messagebox.showerror("Error", "Por favor ingrese una ciudad.")
        return
    
    parametros = {"q": ciudad, "appid": API_KEY, "units": "metric", "lang": "es"}
    
    try:
        respuesta_actual = requests.get(BASE_URL, params=parametros)
        datos_actual = respuesta_actual.json()
        
        respuesta_forecast = requests.get(FORECAST_URL, params=parametros)
        datos_forecast = respuesta_forecast.json()

        if respuesta_actual.status_code == 200 and respuesta_forecast.status_code == 200:
            temperatura = datos_actual["main"]["temp"]
            clima = datos_actual["weather"][0]["description"]
            humedad = datos_actual["main"]["humidity"]
            viento = datos_actual["wind"]["speed"]
            icono = datos_actual["weather"][0]["icon"]
            ciudad_nombre = datos_actual["name"]

            # Descargar el icono del clima
            imagen_url = ICON_URL.format(icono)
            img_data = requests.get(imagen_url).content
            with open("icon.png", "wb") as f:
                f.write(img_data)

            img = Image.open("icon.png").resize((100, 100), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            label_icon.configure(image=img)
            label_icon.image = img

            resultado.configure(text=f"🌍 {ciudad_nombre}\n🌡️ {temperatura}°C\n☁️ {clima.capitalize()}\n💧 Humedad: {humedad}%\n💨 Viento: {viento} m/s")

            # Pronóstico de 5 días
            pronostico_texto = "📅 Próximos días:\n"
            for punto in datos_forecast["list"][::8]:  
                fecha = punto["dt_txt"].split(" ")[0]  
                dia_semana = convertir_fecha_a_dia(fecha)  
                temp_max = punto["main"]["temp_max"]
                temp_min = punto["main"]["temp_min"]
                pronostico_texto += f"{dia_semana}: {temp_max}°C ↑  {temp_min}°C ↓\n"

            label_forecast.configure(text=pronostico_texto)

        else:
            messagebox.showerror("Error", "Ciudad no encontrada.")
    
    except requests.exceptions.RequestException:
        messagebox.showerror("Error", "No se pudo conectar a la API.")

# 🔹 Entrada de ciudad
titulo = ctk.CTkLabel(frame, text="🌎 Ciudad", font=("Arial", 22, "bold"))
titulo.pack(pady=10)

entrada_ciudad = ctk.CTkEntry(frame, font=("Arial", 16), width=250, justify="center")
entrada_ciudad.pack(pady=5)

# 🔹 Botón de búsqueda
boton_buscar = ctk.CTkButton(frame, text="🔍 Buscar Clima", font=("Arial", 14), command=obtener_clima)
boton_buscar.pack(pady=10)

# 🔹 Botón para agregar a favoritos
boton_favorito = ctk.CTkButton(frame, text="⭐ Agregar a Favoritos", font=("Arial", 14), command=agregar_favorito)
boton_favorito.pack(pady=10)

# 🔹 Icono del clima
label_icon = ctk.CTkLabel(frame, text="")
label_icon.pack()

# 🔹 Información del clima
resultado = ctk.CTkLabel(frame, text="", font=("Arial", 18, "bold"))
resultado.pack(pady=15)

# 🔹 Pronóstico de 5 días
label_forecast = ctk.CTkLabel(frame, text="", font=("Arial", 16), fg_color="gray", corner_radius=10, width=350, height=80)
label_forecast.pack(pady=10)

# 🔹 Lista de favoritos
ctk.CTkLabel(frame, text="📌 Favoritos", font=("Arial", 18, "bold")).pack(pady=5)
lista_favoritos = ctk.CTkTextbox(frame, height=100, width=300, font=("Arial", 14), fg_color="#2E2E2E", corner_radius=10)
lista_favoritos.pack(pady=5)

# 🔹 Obtener ubicación automática al abrir
obtener_ubicacion()

# 🔹 Ejecutar la ventana
ventana.mainloop()

import requests
import customtkinter as ctk
import tkinter as tk
from datetime import datetime

# 🔥 PUT YOUR ESP32 IP HERE
ESP32_IP = "http://10.230.0.46"    # CHANGE THIS

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("900x600")
app.title("Aquaponics Smart Dashboard")

# ---------------- HEADER ----------------
title = ctk.CTkLabel(app, text="🌿 Aquaponics Smart Monitor",
                     font=("Arial", 26, "bold"))
title.pack(pady=10)

time_label = ctk.CTkLabel(app, text="")
time_label.pack()

status_label = ctk.CTkLabel(app, text="Connecting...",
                            text_color="yellow")
status_label.pack(pady=5)

canvas = tk.Canvas(app, width=850, height=420,
                   bg="#1e1e1e", highlightthickness=0)
canvas.pack(pady=20)


# ---------------- DRAW GAUGE ----------------
def draw_gauge(x, y, radius, label):

    # Background ring
    canvas.create_oval(x-radius, y-radius,
                       x+radius, y+radius,
                       outline="#2e2e2e",
                       width=15)

    canvas.create_text(x, y-radius-25,
                       text=label,
                       fill="white",
                       font=("Arial", 16, "bold"))

    value_text = canvas.create_text(x, y,
                                    text="--",
                                    fill="white",
                                    font=("Arial", 22, "bold"))

    return value_text


# Create Gauges
temp_text = draw_gauge(200, 250, 100, "🌡 Temperature (°C)")
ph_text = draw_gauge(425, 250, 100, "🧪 pH Level")
moist_text = draw_gauge(650, 250, 100, "🌱 Moisture")

warning_label = ctk.CTkLabel(app, text="", font=("Arial", 16))
warning_label.pack(pady=10)


# ---------------- DRAW ARC ----------------
def draw_arc(x, y, radius, percent, color):

    extent = percent * 360

    canvas.create_arc(x-radius, y-radius,
                      x+radius, y+radius,
                      start=90, extent=-extent,
                      style="arc",
                      outline=color,
                      width=15,
                      tags="arc")


# ---------------- UPDATE FUNCTION ----------------
def update_data():
    try:
        canvas.delete("arc")

        response = requests.get(ESP32_IP + "/data", timeout=3)
        data = response.json()

        temperature = float(data["temperature"])
        ph = float(data["ph"])
        moisture = float(data["moisture"])

        time_label.configure(text="Time: " +
                             datetime.now().strftime("%H:%M:%S"))
        status_label.configure(text="ESP32 Connected ✔",
                               text_color="green")

        # -------- TEMPERATURE --------
        temp_percent = max(0, min(temperature / 50, 1))

        if temperature < 22:
            temp_color = "#00bfff"
        elif temperature <= 30:
            temp_color = "#00ff66"
        else:
            temp_color = "#ff3333"

        canvas.itemconfig(temp_text, text=f"{temperature:.2f}")
        draw_arc(200, 250, 100, temp_percent, temp_color)

        # -------- pH (PH PAPER COLOR LOGIC) --------
        ph_percent = max(0, min(ph / 14, 1))

        if ph <= 3:
            ph_color = "#ff0000"      # Strong Acid
        elif ph <= 6:
            ph_color = "#ff8800"      # Acidic
        elif ph <= 7.5:
            ph_color = "#00ff66"      # Neutral
        elif ph <= 10:
            ph_color = "#0088ff"      # Basic
        else:
            ph_color = "#aa00ff"      # Strong Base

        canvas.itemconfig(ph_text, text=f"{ph:.2f}")
        draw_arc(425, 250, 100, ph_percent, ph_color)

        # -------- MOISTURE --------
        moist_percent = max(0, min(moisture / 4095, 1))

        if moisture < 1500:
            moist_color = "#ff3333"
        elif moisture < 3000:
            moist_color = "#ffaa00"
        else:
            moist_color = "#00ff66"

        canvas.itemconfig(moist_text, text=f"{moisture:.0f}")
        draw_arc(650, 250, 100, moist_percent, moist_color)

        # -------- WARNINGS --------
        warning_text = ""

        if temperature < 22 or temperature > 30:
            warning_text += "⚠ Temperature Out of Range!\n"

        if ph < 6.5 or ph > 7.5:
            warning_text += "⚠ pH Out of Ideal Range!\n"

        if moisture < 1500:
            warning_text += "⚠ Soil Too Dry!\n"

        if warning_text == "":
            warning_label.configure(text="✅ All Parameters Normal",
                                    text_color="lightgreen")
        else:
            warning_label.configure(text=warning_text,
                                    text_color="red")

    except Exception as e:
        print("Error:", e)
        status_label.configure(text="ESP32 Not Reachable ❌",
                               text_color="red")

    app.after(2000, update_data)


update_data()
app.mainloop()

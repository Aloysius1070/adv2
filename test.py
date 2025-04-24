import customtkinter as ctk
import tkinter as tk
from PIL import Image
from customtkinter import CTkImage
import os

# === CONFIG ===
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 500
CAR_WIDTH = 60
CAR_HEIGHT = 30
CAR_SPEED = 5
MATCHED_IMAGE_PATH = "best_match_result.jpg"
ADVERSARIAL_IMAGE_PATH = "adversarial_image.jpg"

# === Appearance ===
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

# === File Check ===
if not os.path.exists(MATCHED_IMAGE_PATH):
    raise FileNotFoundError("❌ 'best_match_result.jpg' not found.")
if not os.path.exists(ADVERSARIAL_IMAGE_PATH):
    raise FileNotFoundError("❌ 'adversarial_image.jpg' not found.")

# === Main Window ===
root = ctk.CTk()
root.title("🚗 Smart Car Traffic Simulation")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT + 100}")
root.resizable(False, False)

# === Flags ===
image_shown = car_stopped = crashed = car_resumed = False

# === Header ===
title = ctk.CTkLabel(root, text="🚘 Modern Autonomous Car Simulation", font=ctk.CTkFont(size=24, weight="bold"))
title.pack(pady=15)

# === Main Frame ===
main_frame = ctk.CTkFrame(root)
main_frame.pack(padx=20, pady=10, fill="both", expand=True)

# === Canvas Frame ===
canvas_frame = ctk.CTkFrame(main_frame, corner_radius=15)
canvas_frame.grid(row=0, column=0, padx=(10, 20), pady=10)

canvas = tk.Canvas(canvas_frame, width=800, height=WINDOW_HEIGHT, bg="#dfe4ea", highlightthickness=0)
canvas.pack()

# === Draw Road ===
canvas.create_rectangle(0, 200, 800, 260, fill="#2f3542")  # Road base
# Lane lines
for x in range(0, 800, 80):
    canvas.create_line(x + 20, 230, x + 50, 230, fill="white", width=3, dash=(10, 10))

# === Draw Modern Traffic Signal ===
signal_x = 700
canvas.create_rectangle(signal_x, 150, signal_x + 40, 260, fill="#2d3436", outline="black", width=2)

# Red, Yellow, Green Lights
canvas.create_oval(signal_x + 10, 160, signal_x + 30, 180, fill="red", outline="")
canvas.create_oval(signal_x + 10, 190, signal_x + 30, 210, fill="gray25", outline="")
canvas.create_oval(signal_x + 10, 220, signal_x + 30, 240, fill="gray25", outline="")

# === Car ===
car = canvas.create_rectangle(0, 210, CAR_WIDTH, 210 + CAR_HEIGHT, fill="#0984e3", outline="black")

# === Sidebar ===
side_panel = ctk.CTkFrame(main_frame, width=200)
side_panel.grid(row=0, column=1, pady=10, sticky="nsew")

status_label = ctk.CTkLabel(side_panel, text="Status: 🚦 Driving", font=ctk.CTkFont(size=16))
status_label.pack(pady=(10, 5))

prediction_label = ctk.CTkLabel(side_panel, text="🎯 Prediction: -", font=ctk.CTkFont(size=14))
prediction_label.pack(pady=(5, 5))

confidence_label = ctk.CTkLabel(side_panel, text="📊 Confidence: -", font=ctk.CTkFont(size=14))
confidence_label.pack(pady=(5, 15))

image_label = ctk.CTkLabel(side_panel, text="Preview", font=ctk.CTkFont(size=14, weight="bold"))
image_label.pack(pady=(10, 5))

image_preview = ctk.CTkLabel(side_panel, text="")
image_preview.pack()

# === Restart Button ===
def restart_simulation():
    global image_shown, car_stopped, crashed, car_resumed
    canvas.coords(car, 0, 210, CAR_WIDTH, 210 + CAR_HEIGHT)
    canvas.itemconfig(car, fill="#0984e3")
    status_label.configure(text="Status: 🚦 Driving")
    prediction_label.configure(text="🎯 Prediction: -")
    confidence_label.configure(text="📊 Confidence: -")
    image_preview.configure(image=None, text="")
    image_shown = car_stopped = crashed = car_resumed = False
    move_car()

ctk.CTkButton(side_panel, text="🔁 Restart", command=restart_simulation).pack(pady=20)

# === Simulation Functions ===

def show_matched_image():
    global image_preview
    img = Image.open(MATCHED_IMAGE_PATH)
    ct_img = CTkImage(light_image=img, size=(180, 120))
    image_preview.configure(image=ct_img, text="")
    image_preview.image = ct_img
    status_label.configure(text="Status: 🛑 Stopped at Signal")
    root.after(5000, resume_car_and_crash)

def resume_car_and_crash():
    global car_resumed
    car_resumed = True
    move_car()
    root.after(1000, simulate_crash)

def simulate_crash():
    global crashed
    if not crashed:
        canvas.itemconfig(car, fill="red")
        canvas.create_text(400, 100, text="💥 Crash!", font=("Arial", 28, "bold"), fill="red")
        status_label.configure(text="Status: 💥 Crash!")
        crashed = True
        show_adversarial_image()

def move_car():
    global image_shown, car_stopped, car_resumed
    if not car_stopped:
        canvas.move(car, CAR_SPEED, 0)
        pos = canvas.coords(car)
        if not image_shown and pos and pos[2] >= signal_x - 30:
            show_matched_image()
            image_shown = True
            car_stopped = True
        root.after(50, move_car)
    elif car_resumed and not crashed:
        canvas.move(car, CAR_SPEED, 0)
        root.after(50, move_car)

def show_adversarial_image():
    adv_window = ctk.CTkToplevel(root)
    adv_window.title("⚠️ Adversarial Detection")
    adv_window.geometry("520x540")
    adv_window.resizable(False, False)

    predicted_class, confidence = read_adversarial_info()
    prediction_label.configure(text=f"🎯 Prediction: {predicted_class}")
    confidence_label.configure(text=f"📊 Confidence: {confidence:.2f}")

    title = ctk.CTkLabel(adv_window, text="⚠️ Adversarial Image", font=ctk.CTkFont(size=20, weight="bold"), text_color="red")
    title.pack(pady=15)

    if os.path.exists(ADVERSARIAL_IMAGE_PATH):
        img = Image.open(ADVERSARIAL_IMAGE_PATH)
        ct_img = CTkImage(light_image=img, size=(400, 300))
        img_label = ctk.CTkLabel(adv_window, image=ct_img, text="")
        img_label.image = ct_img
        img_label.pack(pady=10)

    info = ctk.CTkLabel(adv_window, text=f"🎯 {predicted_class}\n📊 {confidence:.2f}", font=ctk.CTkFont(size=16), text_color="black")
    info.pack(pady=10)

def read_adversarial_info(filepath="adversarial_info.txt"):
    try:
        with open(filepath, "r") as f:
            line = f.readline().strip()
            if ',' in line:
                class_name, confidence = line.split(',')
                return class_name.strip(), float(confidence)
            else:
                raise ValueError("Invalid format.")
    except Exception as e:
        print(f"Error reading adversarial info: {e}")
        return "Unknown", 0.0

# === Start Simulation ===
merged_class_name, merged_confidence = read_adversarial_info()
print(f"✅ Loaded: {merged_class_name}, Confidence: {merged_confidence:.2f}")
move_car()
root.mainloop()

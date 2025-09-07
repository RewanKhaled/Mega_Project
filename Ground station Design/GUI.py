import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import pandas as pd
import os
import subprocess
import sys
import joblib
import sounddevice as sd
import numpy as np
from python_speech_features import mfcc
import serial
import threading

# ----------------- Config -----------------
CSV_FILE = "sensor_data_log.csv"
MODEL_FILE = "voice_model.pkl"

# Load trained voice model
model = joblib.load(MODEL_FILE)

# Serial connection to STM32 
ser = serial.Serial(port="COM3", baudrate=9600, timeout=1)

# ----------------- Logging Helpers -----------------
def log_data(entry):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([[timestamp, entry]], columns=["Timestamp", "Data"])
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, mode='w', header=True, index=False)

# ----------------- Serial Listener -----------------
def listen_serial():
    while True:
        try:
            line = ser.readline().decode().strip()
            if line:
                if line == "OBJECT":
                    root.after(0, lambda: object_detected())
                elif line.startswith("TEMP:"):
                    temp = line.split(":")[1]
                    root.after(0, lambda: update_temp(temp))
                elif line.startswith("LIGHT:"):
                    light = line.split(":")[1]
                    root.after(0, lambda: update_light(light))
                else:
                    print("Received:", line)
        except:
            break

def object_detected():
    messagebox.showwarning("Alert", "🚨 Object Detected!")
    log_data("Object Detected")

def update_temp(value):
    lbl_temp.config(text=f"Temperature: {value} °C")
    log_data(f"Temperature: {value} °C")

def update_light(value):
    lbl_light.config(text=f"Light Intensity: {value}")
    log_data(f"Light Intensity: {value}")

# ----------------- Voice Control -----------------
def listen_and_predict(duration=2, fs=16000):
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    audio = audio.flatten()
    features = mfcc(audio, fs, numcep=13)
    mfcc_mean = np.mean(features, axis=0).reshape(1, -1)
    return model.predict(mfcc_mean)[0]

def voice_control():
    status_var.set("🎙 Speak ON or OFF...")
    root.update()
    pred = listen_and_predict()
    if pred == 1:
        status_var.set("🟢 System turned ON (voice)")
        log_data("Voice Command: ON")
        ser.write(b"ON\n")
    else:
        status_var.set("🔴 System turned OFF (voice)")
        log_data("Voice Command: OFF")
        ser.write(b"OFF\n")

# ----------------- Manual Requests -----------------
def request_temp():
    if ser:
        ser.write(b"GET_TEMP\n")
        log_data("Requested Temperature")

def request_light():
    if ser:
        ser.write(b"GET_LIGHT\n")
        log_data("Requested Light")

# ----------------- History with Search -----------------
def show_history():
    history_window = tk.Toplevel(root)
    history_window.title("System Data History")
    history_window.geometry("500x400")

    # Search box
    search_var = tk.StringVar()
    tk.Label(history_window, text="Search:").pack(pady=5)
    search_entry = tk.Entry(history_window, textvariable=search_var)
    search_entry.pack(pady=5)

    # Treeview
    tree = ttk.Treeview(history_window, columns=("Time", "Data"), show="headings")
    tree.heading("Time", text="Timestamp")
    tree.heading("Data", text="Data")
    tree.pack(fill="both", expand=True)

    def load_data(filter_text=""):
        for row in tree.get_children():
            tree.delete(row)

        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            for _, row in df.iterrows():
                if filter_text.lower() in str(row["Data"]).lower():
                    tree.insert("", "end", values=(row["Timestamp"], row["Data"]))
        else:
            messagebox.showinfo("History", "No data found yet!")

    def on_search(*args):
        load_data(search_var.get())

    search_var.trace("w", on_search)
    load_data()

# ----------------- Open CSV -----------------
def open_csv():
    if not os.path.exists(CSV_FILE):
        messagebox.showerror("Error", "CSV file does not exist yet!")
        return
    try:
        if sys.platform.startswith("win"):
            os.startfile(CSV_FILE)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", CSV_FILE])
        else:
            subprocess.call(["xdg-open", CSV_FILE])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open file: {e}")

# ----------------- GUI Layout -----------------
root = tk.Tk()
root.title("Satellite Ground Station")
root.geometry("370x360")

status_var = tk.StringVar(value="System Idle")
tk.Label(root, textvariable=status_var, font=("Arial", 14), fg="blue").pack(pady=10)

# Object Detection Box
frame_object = tk.LabelFrame(root, text="Object Detection", padx=10, pady=10)
frame_object.pack(fill="x", padx=10, pady=5)
btn_obj = tk.Button(frame_object, text="🚨 Simulate Object Detection Manually", command=object_detected, bg="pink")
btn_obj.pack(fill="x")

# Voice Control Box
frame_voice = tk.LabelFrame(root, text="Voice Control", padx=10, pady=10)
frame_voice.pack(fill="x", padx=10, pady=5)
btn_voice = tk.Button(frame_voice, text="🎙 Start Voice Command", command=voice_control, bg="pink")
btn_voice.pack(fill="x")

# Sensor Readings Box
frame_row = tk.Frame(root)
frame_row.pack(padx=10, pady=5, fill="x")
frame_sensors = tk.LabelFrame(frame_row, text="Sensor Readings", padx=5, pady=5)
frame_sensors.grid(row=0, column=0, padx=5, pady=5, sticky="n")
lbl_temp = tk.Label(frame_sensors, text="Temperature: ---", font=("Arial", 10))
lbl_temp.pack(pady=2)
btn_temp = tk.Button(frame_sensors, text="Get Temperature", command=request_temp, 
                     font=("Arial", 10), width=18, height=1, fg="blue",)
btn_temp.pack(pady=2)
lbl_light = tk.Label(frame_sensors, text="Light Intensity: ---", font=("Arial", 10))
lbl_light.pack(pady=2)
btn_light = tk.Button(frame_sensors, text="Get Light Intensity", command=request_light,
                      font=("Arial", 10), width=18, height=1, fg="blue",)
btn_light.pack(pady=2)

# Data Management Box
frame_data = tk.LabelFrame(frame_row, text="Data Management", padx=5, pady=5)
frame_data.grid(row=0, column=1, padx=5, pady=5, sticky="n")

btn_history = tk.Button(frame_data, text="📜 Show History", command=show_history,
                        font=("Arial", 10), width=18, height=1, fg="green")
btn_history.pack(pady=2)

btn_open_csv = tk.Button(frame_data, text="📂 Open CSV File", command=open_csv,
                         font=("Arial", 10), width=18, height=1, fg="green")
btn_open_csv.pack(pady=2)


# ----------------- Run Serial Listener in Background -----------------
threading.Thread(target=listen_serial, daemon=True).start()

root.mainloop()
ser.close()

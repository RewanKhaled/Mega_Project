# Satellite System Simulation 🚀

## 📌 Overview
This project simulates a **satellite system** using a microcontroller (STM32F103C6T6) and a ground station (laptop with Python GUI).  
The system monitors **temperature**, **light intensity**, and **object detection** (radar with ultrasonic + servo), and communicates data to the ground station.

## 🛰️ Satellite Segment
- **Temperature Sensor** → Controls 3 red LEDs depending on value.  
- **Light Intensity Sensor (Photoresistor)** → Controls white LED.  
- **Radar System (Ultrasonic + Servo motor)** → Detects nearby objects, activates green LED.  
- **Microcontroller**: STM32F103C6T6 (Blue Pill).  

## 🖥️ Ground Station
- GUI built with **Tkinter (Python)**.  
- **Object Detection Alerts** when ultrasonic sensor triggers.  
- **Voice Control** → Turn system ON/OFF using custom ML model.  
- **Sensor Readings** → Request temperature & light data anytime.  
- **Data Logging** → Store and review sensor history.  

## 📂 Tools & Components
- STM32F103C6T6 (Blue Pill)  
- Servo motor, Ultrasonic sensor  
- Temperature sensor, Photoresistor  
- LEDs (red, green, white)  
- Python (Tkinter, ML for voice recognition)  

## 🎥 Demo
[▶️ Watch the demo video on Google Drive]()

---

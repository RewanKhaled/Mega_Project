import serial
import time

# Adjust COM port and baudrate to match your STM32 setup
ser = serial.Serial(port="COM3", baudrate=9600, timeout=1)

print("Listening for object detection data from STM32...")

try:
    while True:
        line = ser.readline().decode().strip()
        if line:
            if line == "OBJECT":
                print("🚨 Object Detected!")
            elif line == "CLEAR":
                print("✅ No Object")
            else:
                print("Received:", line)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopped by user")
finally:
    ser.close()

import serial
import time

PORT = "/dev/serial0"
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(1)

print("Reading GPS NMEA... (Ctrl+C to stop)")
while True:
    line = ser.readline().decode("ascii", errors="ignore").strip()
    if line.startswith("$"):
        print(line)
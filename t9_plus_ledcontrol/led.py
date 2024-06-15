import serial
import time

# A=Mode
#   0x04: Off
#   0x05: Auto
#   0x01: Rainbow
#   0x02: Breating
#   0x03: Color cycle

# B=Brightness
#   0x05: 1
#   0x04: 2
#   0x03: 3
#   0x02: 4
#   0x01: 5

# C=Speed
#   0x05: 1
#   0x04: 2
#   0x03: 3
#   0x02: 4
#   0x01: 5

# D=Check Digit
#   (0xfa+A+B+C) & 0xff

def calculate_checksum(data):
    return (0xfa + sum(data)) & 0xff

def control(port, baudrate, mode, brightness, speed, delay=0.005):
    try:
        with serial.Serial(port, baudrate) as s:
            data = [mode, brightness, speed]
            checksum = calculate_checksum(data)
            packet = [0xfa] + data + [checksum]
            for byte in packet:
                s.write(byte.to_bytes(1, 'big'))
                time.sleep(delay)
        print("Data sent successfully.")
    except serial.SerialException as e:
        print(f"Failed to send data: {e}")
        raise

if __name__ == "__main__":
    control("COM3", 9600, 0x04, 0x05, 0x05)
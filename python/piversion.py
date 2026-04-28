from flask import Flask, request
import time
import threading
from smbus2 import SMBus

# ---- LCD DRIVER (for 0x3e LCD) ----
class GroveLcd:
    def __init__(self, addr=0x3E, bus_num=1):
        self.bus = SMBus(bus_num)
        self.addr = addr

        self.command(0x02)
        time.sleep(0.1)
        self.command(0x0C)
        self.command(0x28)
        self.command(0x01)
        time.sleep(0.05)

    def command(self, cmd):
        self.bus.write_byte_data(self.addr, 0x80, cmd)

    def write_char(self, char):
        self.bus.write_byte_data(self.addr, 0x40, ord(char))

    def clear(self):
        self.command(0x01)
        time.sleep(0.05)

    def set_cursor(self, row, col):
        self.command((0x40 * row) + col + 0x80)

    def print(self, text):
        for c in text:
            self.write_char(c)

# ---- INIT ----
app = Flask(__name__)
lcd = GroveLcd()

def set_text(text):
    lcd.clear()
    lines = text.split("\n")
    for i, line in enumerate(lines[:2]):
        lcd.set_cursor(i, 0)
        lcd.print(line[:16])

# Initial display
set_text("System Ready")

last_message_time = 0
display_timeout = 5  # seconds

# ---- RESET DISPLAY ----
def reset_display():
    set_text("System Ready")

# ---- BUS PASSED ----
@app.route("/bus_passed")
def bus_passed():
    global last_message_time

    set_text("BUS PASSED\nTake Action!")
    print("Bus passed signal received")

    last_message_time = time.time()
    return "OK"

# ---- MOTION ----
@app.route("/motion")
def motion():
    global last_message_time

    state = request.args.get("state")

    if state == "motion":
        set_text("Motion Detected!")
        print("Motion detected")
    else:
        set_text("All Clear")
        print("No motion")

    last_message_time = time.time()
    return "OK"

# ---- AUTO RESET ----
def monitor_timeout():
    global last_message_time

    while True:
        if last_message_time != 0:
            if time.time() - last_message_time > display_timeout:
                reset_display()
                last_message_time = 0
        time.sleep(1)

# ---- START ----
if __name__ == "__main__":
    t = threading.Thread(target=monitor_timeout, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=8000)
from flask import Flask, request
from grove_rgb_lcd import *
import time

app = Flask(__name__)

# ---- LCD INIT ----
setRGB(0, 0, 255)
setText("System Ready")

last_message_time = 0
display_timeout = 5  # seconds before reverting to idle

# ---- Helper: reset screen ----
def reset_display():
    setRGB(0, 0, 255)
    setText("System Ready")

# ---- BUS PASSED ENDPOINT ----
@app.route("/bus_passed")
def bus_passed():
    global last_message_time

    setRGB(255, 0, 0)
    setText("BUS PASSED\nTake Action!")
    print("Bus passed signal received")

    last_message_time = time.time()
    return "OK"

# ---- MOTION ENDPOINT ----
@app.route("/motion")
def motion():
    global last_message_time

    state = request.args.get("state")

    if state == "motion":
        setRGB(255, 165, 0)  # orange
        setText("Motion Detected!")
        print("Motion detected")
    else:
        setRGB(0, 255, 0)
        setText("All Clear")
        print("No motion")

    last_message_time = time.time()
    return "OK"

# ---- BACKGROUND LOOP TO RESET DISPLAY ----
def monitor_timeout():
    global last_message_time

    while True:
        if last_message_time != 0:
            if time.time() - last_message_time > display_timeout:
                reset_display()
                last_message_time = 0
        time.sleep(1)

# ---- START SERVER + BACKGROUND THREAD ----
if __name__ == "__main__":
    import threading

    t = threading.Thread(target=monitor_timeout, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=8000)
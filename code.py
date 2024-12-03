import os
import board
import displayio
import terminalio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
import microcontroller

# Initialize display
display = board.DISPLAY

# Initialize joystick buttons
joystick_up = DigitalInOut(board.SWITCH_UP)
joystick_down = DigitalInOut(board.SWITCH_DOWN)
joystick_left = DigitalInOut(board.SWITCH_LEFT)
joystick_right = DigitalInOut(board.SWITCH_RIGHT)
joystick_press = DigitalInOut(board.SWITCH_PRESS)

for button in [joystick_up, joystick_down, joystick_left, joystick_right, joystick_press]:
    button.direction = Direction.INPUT
    button.pull = Pull.UP

# Function to deinitialize joystick buttons
def deinitialize_joystick():
    for button in [joystick_up, joystick_down, joystick_left, joystick_right, joystick_press]:
        button.deinit()

# Function to list `.py` files in the /Programs directory
def list_scripts(path="/Programs"):
    try:
        files = os.listdir(path)
        print(f"Files in {path}: {files}")  # Debugging statement
        return [file for file in files if file.endswith(".py")]
    except OSError:
        print(f"Directory {path} not found!")
        return []

# Function to draw the file list
def draw_list(scripts, selected_index, max_items=5):
    group = displayio.Group()

    # Background
    bg = Rect(0, 0, display.width, display.height, fill=0x000000)
    group.append(bg)

    # Display script names in a scrolling list
    start_index = max(0, selected_index - max_items + 1)
    end_index = min(len(scripts), start_index + max_items)

    for i, script in enumerate(scripts[start_index:end_index]):
        y = 10 + (i * 20)  # Spacing between items
        color = 0xFFFFFF if i + start_index == selected_index else 0xAAAAAA
        text = label.Label(terminalio.FONT, text=script, color=color, x=10, y=y)
        group.append(text)

    display.root_group = group

# Function to run a selected script
def run_script(script_path):
    try:
        # Execute the selected script
        with open(script_path, "r") as script_file:
            code = script_file.read()
        exec(code, {"__name__": "__main__"})
    except Exception as e:
        print(f"Error running {script_path}: {e}")

# Main program loop
def main():
    # List available scripts
    scripts = list_scripts()
    if not scripts:
        print("No scripts found in /Programs!")
        return

    selected_index = 0

    while True:
        draw_list(scripts, selected_index)
    
        # Navigation logic
        if not joystick_up.value:
            selected_index = max(0, selected_index - 1)
        elif not joystick_down.value:
            selected_index = min(len(scripts) - 1, selected_index + 1)
        elif not joystick_press.value:
            selected_script = f"/Programs/{scripts[selected_index]}"
            deinitialize_joystick()
            display.root_group = None  # Clear the display
            run_script(selected_script)
            break

# Start the application
main()

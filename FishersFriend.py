import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Entry, IntVar
from ttkthemes import ThemedTk
import threading
import pyautogui
import time
import random
from PIL import Image, ImageTk
from io import BytesIO
import _tkinter
import os
from pathlib import Path

import random as rd
import numpy as np
import pytweening
from humancurve import HumanCurve

# ASCII art for "Fishers Friend"
ascii_art = """
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░█▀▀░▀█▀░█▀▀░█░█░█▀▀░█▀▄░█▀▀░░░░░░░░░
░░░░░░░░█▀▀░░█░░▀▀█░█▀█░█▀▀░█▀▄░▀▀█░░░░░░░░░
░░░░░░░░▀░░░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀░▀░▀▀▀░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░█▀▀░█▀▄░▀█▀░█▀▀░█▀█░█▀▄░░░░░░░░░░░
░░░░░░░░░░█▀▀░█▀▄░░█░░█▀▀░█░█░█░█░░░░░░░░░░░
░░░░░░░░░░▀░░░▀░▀░▀▀▀░▀▀▀░▀░▀░▀▀░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
"""

# Global variables
running = False
running_lock = threading.Lock()  # Thread lock for the 'running' variable

# You can set the initial threshold value as needed
bait_movement_threshold = 8
confidence_values = {
    'Fishing Rod': 0.75,
    'Bait': 0.75
}

# Function to get color for a specific label
color_mapping = {
    'Fishing Rod': 'orange',
    'Bait': 'purple',
    'Looking for fish': 'blue',
}
# Paths to the images
fishing_rod_path = ""
bait_paths = []

# Global variable to store the screenshot image
screenshot_area = {'value': None}

# Dictionary to store entry and slider variables for each template
confidence_entries = {}

# Define the MouseUtils class
class MouseUtils:
    @staticmethod
    def move_to(destination: tuple, **kwargs):
        offsetBoundaryX = kwargs.get("offsetBoundaryX", 100)
        offsetBoundaryY = kwargs.get("offsetBoundaryY", 100)
        knotsCount = kwargs.get("knotsCount", MouseUtils.__calculate_knots(destination))
        distortionMean = kwargs.get("distortionMean", 1)
        distortionStdev = kwargs.get("distortionStdev", 1)
        distortionFrequency = kwargs.get("distortionFrequency", 0.5)
        tween = kwargs.get("tweening", pytweening.easeOutQuad)

        # Set mouseSpeed to a random value based on the provided speed parameter
        mouse_speed_param = kwargs.get("mouseSpeed", "fast")  # Default to "fast" if not provided
        mouseSpeed = MouseUtils.__get_mouse_speed(mouse_speed_param)
        
        dest_x = destination[0]
        dest_y = destination[1]

        start_x, start_y = pyautogui.position()
        for curve_x, curve_y in HumanCurve(
            (start_x, start_y),
            (dest_x, dest_y),
            offsetBoundaryX=offsetBoundaryX,
            offsetBoundaryY=offsetBoundaryY,
            knotsCount=knotsCount,
            distortionMean=distortionMean,
            distortionStdev=distortionStdev,
            distortionFrequency=distortionFrequency,
            tween=tween,
            targetPoints=mouseSpeed,
        ).points:
            pyautogui.moveTo((curve_x, curve_y))
            start_x, start_y = curve_x, curve_y

    @staticmethod
    def __calculate_knots(destination: tuple):
        distance = np.sqrt((destination[0] - pyautogui.position()[0]) ** 2 + (destination[1] - pyautogui.position()[1]) ** 2)
        # Choose knots randomly between 1 and 6
        res = random.randint(1, 6)
        return min(res, 3)

    @staticmethod
    def move_rel(x: int, y: int, x_var: int = 0, y_var: int = 0, **kwargs):
        if x_var != 0:
            x += np.random.randint(-x_var, x_var)
        if y_var != 0:
            y += np.random.randint(-y_var, y_var)
        MouseUtils.move_to((pyautogui.position()[0] + x, pyautogui.position()[1] + y), **kwargs)

    @staticmethod
    def __get_mouse_speed(speed: int) -> int:
        if speed == "slowest":
            return rd.randint(85, 100)
        elif speed == "slow":
            return rd.randint(65, 80)
        elif speed == "medium":
            return rd.randint(45, 60)
        elif speed == "fast":
            return rd.randint(20, 40)
        elif speed == "fastest":
            return rd.randint(10, 15)
        else:
            raise ValueError("Invalid mouse speed. Try 'slowest', 'slow', 'medium', 'fast', or 'fastest'.")


# Updated move_to_location function using MouseUtils
def move_to_location(x, y, speed='fast'):
    current_x, current_y = pyautogui.position()
    distance = ((x - current_x) ** 2 + (y - current_y) ** 2) ** 0.5
    deviation_x = random.uniform(-5, 5)
    deviation_y = random.uniform(-5, 5)
    duration = distance / 1000
    if speed == 'fast':
        duration /= 2

    # Use MouseUtils.move_to for human-like movements
    MouseUtils.move_to((x + deviation_x, y + deviation_y), mouseSpeed=speed)

# Updated move_to_bait_bottom_right function using MouseUtils
def move_to_bait_bottom_right(bait_location, speed='fast'):
    x = bait_location.left + bait_location.width
    y = bait_location.top + bait_location.height

    # Use MouseUtils.move_to for human-like movements
    MouseUtils.move_to((x, y), mouseSpeed=speed)


# Function to find a template on the screen
def find_template(template_info, timeout=10, label="Template"):
    start_time = time.time()
    while time.time() - start_time < timeout:
        for template_image, confidence in template_info:
            location = pyautogui.locateOnScreen(template_image, confidence=confidence)
            if location is not None:
                log_output(f"{label} found", color=get_color_for_label(label), bold=True)
                return location
    return None

# Function to execute the main loop in a separate thread
def execute_code():
    global running
    with running_lock:
        running = True
    log_output("Starting", color="green", bold=True)

    # Check if fishing_rod_path and bait_paths are empty
    if not fishing_rod_path and not bait_paths:
        messagebox.showinfo("No Images Set", "Please set Fishing Rod and Bait images first.")
        log_output("Program Stopped", color="red", bold=True)
        return

    # Initialize counters for random actions
    random_action_counter = random.randint(1, 15)
    current_loop = 0

    while True:
        with running_lock:
            if not running:
                break
            
        # Increment the loop counter
        current_loop += 1

        # Check if it's time to perform a random action
        if random_actions_checkbox_var.get() and current_loop >= random_action_counter:
            perform_random_action()
            random_action_counter = random.randint(1, 15)
            current_loop = 0

        # Find the fishing rod icon
        fishing_rod_location = find_template([(fishing_rod_path, confidence_values['Fishing Rod'])], label="Fishing Rod")
        if fishing_rod_location is not None:
            # Move to the fishing rod icon and perform a left click
            move_to_location(fishing_rod_location.left + fishing_rod_location.width / 2,
                             fishing_rod_location.top + fishing_rod_location.height / 2)
            pyautogui.click()

            # Wait for 1 second to allow the bait to appear
            time.sleep(2.5)

            # Find the bait icon
            bait_location = find_template(bait_paths, timeout=2, label="Bait")
            if bait_location is not None:
                # Move to the bottom right corner of the bait icon
                move_to_bait_bottom_right(bait_location)

                # Check for bait movement
                original_bait_location = bait_location
                start_time = time.time()
                while time.time() - start_time < 33:  # Timeout set to 35 seconds
                    time.sleep(0.3)  # Wait for 0.3 seconds between each iteration

                    # Find the current bait location
                    bait_location = find_template(bait_paths, timeout=2, label="Bait")
                    if bait_location is not None:
                        log_output("Looking for fish", color="blue")
                        # Calculate the movement distance
                        movement_x = abs(bait_location.left - original_bait_location.left)
                        movement_y = abs(bait_location.top - original_bait_location.top)

                        # Check if the bait has moved by at least the threshold pixels in any direction
                        if movement_x >= bait_movement_threshold or movement_y >= bait_movement_threshold:
                            # Bait moved, perform delayed right-click
                            delay_before_click = toggle_human_reaction_time()  # Using the new function
                            log_output(f"Right-Click will be performed after {delay_before_click:.2f} seconds.", color="green")
                            time.sleep(delay_before_click)  # Delay between 1 and 3 seconds
                            pyautogui.rightClick()
                            log_output("Right-Click performed.", color="green")
                            delay_after_click = random.uniform(3, 5)
                            log_output(f"Sleeping for: {delay_after_click:.2f} seconds...")
                            time.sleep(delay_after_click)  # Sleep between 3 and 5 seconds

                            # Check for the stop condition
                            with running_lock:
                                if not running:
                                    break

                            # Reset the bait location for the next iteration
                            original_bait_location = bait_location
                            break  # Exit the loop and move on with the main loop

                        # Move the cursor to the bottom right corner of the bait continuously
                        # move_to_bait_bottom_right(bait_location)

                        # Check for the stop condition
                        with running_lock:
                            if not running:
                                break

        # Check for the stop condition
        with running_lock:
            if not running:
                break

    log_output("Program Stopped", color="red", bold=True)

# Function to stop the code execution
def stop_execution():
    with running_lock:
        global running
        running = False
    log_output("Trigger Stopping", color="red", bold=True)

# Function to update the confidence values
def update_confidence(template, value, entry_var, slider_var):
    with running_lock:
        # Check if the value has changed
        if confidence_values[template] != value:
            confidence_values[template] = value
            log_output(f"Confidence for {template}: {value:.2f}", color="black", bold=True)
            entry_var.set(f"{value:.2f}")  # Update the associated entry widget with a formatted string
            if slider_var:
                slider_var.set(value)  # Update the associated slider if it exists

# Function to take a screenshot of a selected area
def take_screenshot():
    root.iconify()  # Minimize the main window temporarily

    # Take a screenshot of the entire screen
    screenshot = pyautogui.screenshot()

    # Display the screenshot in a new window
    top = tk.Toplevel(root)
    top.title("Select Area")
    top.attributes("-topmost", True)

    # Convert the screenshot to a Tkinter PhotoImage
    screenshot_image = ImageTk.PhotoImage(screenshot)

    # Create a Canvas to display the screenshot
    canvas = tk.Canvas(top, width=screenshot.width, height=screenshot.height)
    canvas.pack()

    # Display the screenshot on the Canvas
    canvas.create_image(0, 0, anchor=tk.NW, image=screenshot_image)

    # Initialize variables for selection
    start_x, start_y = None, None
    rect_id = None

    # Function to handle mouse press event
    def on_press(event):
        nonlocal start_x, start_y, rect_id
        start_x, start_y = event.x, event.y
        rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red")

    # Function to handle mouse drag event
    def on_drag(event):
        nonlocal rect_id
        canvas.coords(rect_id, start_x, start_y, event.x, event.y)

    # Function to handle mouse release event
    def on_release(event):
        nonlocal start_x, start_y, rect_id
        end_x, end_y = event.x, event.y
        selected_area = (min(start_x, end_x), min(start_y, end_y), max(start_x, end_x), max(start_y, end_y))

        # Crop the screenshot to the selected area
        cropped_screenshot = screenshot.crop(selected_area)

        # Update the global variable with the cropped screenshot
        screenshot_area['value'] = cropped_screenshot

        # Display the cropped screenshot in the main window
        screenshot_image = ImageTk.PhotoImage(cropped_screenshot)
        display_screenshot(screenshot_image)
        log_output("Screenshot taken.")

        # Destroy the "Select Area" window
        top.destroy()

        root.deiconify()  # Restore the main window

    # Bind events to the Canvas
    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    # Wait for the "Select Area" window to be closed
    top.wait_window(top)

# Function to set the image for fishing rod or bait
def set_image(template):
    global fishing_rod_path, bait_paths

    # Trigger the screenshot function
    take_screenshot()

    # Check if a screenshot has been taken
    if screenshot_area['value'] is not None:
        # Ask the user if the screenshot should be set as fishing rod or bait
        answer = messagebox.askyesno("Set Image", f"Do you want to set the taken screenshot as {template}?")
        if answer:
            # Set the image path based on the user's choice
            if template == 'Fishing Rod':
                fishing_rod_path = screenshot_area['value']
            elif template == 'Bait':
                bait_paths = [(screenshot_area['value'], confidence_values['Bait'])]

            log_output(f"{template} image set", color="black", bold=True)

            # Remove the displayed screenshot from the GUI
            screenshot_label.config(image="")
            screenshot_label.image = None
        else:
            log_output(f"{template} image not set", color="black", bold=True)
    else:
        log_output("No screenshot available. Set image failed.", color="red", bold=True)

# Function to display the screenshot in the GUI
def display_screenshot(image):
    screenshot_label.config(image=image)
    screenshot_label.image = image

# Function to log output messages
def log_output(message, color="black", bold=False, initial_message=False):
    # Schedule the GUI update to run in the main thread
    root.after(0, _log_output, message, color, bold, initial_message)

def _log_output(message, color, bold, initial_message):
    tag = color if color != "blue" else "blue"
    console_text.config(state=tk.NORMAL)
    
    # Check if it's the initial message and set the tag to "blue"
    if initial_message:
        tag = "blue"
    
    console_text.insert(tk.END, message + '\n', (tag, bold))
    console_text.config(state=tk.DISABLED)
    console_text.yview(tk.END)
    console_text.update_idletasks()  # Ensure the update is immediate
    made_by_label.pack(side=tk.RIGHT, padx=5, pady=5) # Adjust the row and column as needed

def get_color_for_label(label):
    color_mapping = {
        'Fishing Rod': 'orange',
        'Bait': 'purple',
        'Looking for fish': 'blue',
    }
    print(f"Debug: Label '{label}'")
    return color_mapping.get(label, 'black')

# Function to create and configure sliders and entry widgets
def create_slider_and_entry(template, row, entry_var, slider_var):
    ttk.Label(confidence_frame, text=f"{template}:").grid(row=row, column=0, pady=5, sticky=tk.E)

    # Create and configure a slider
    confidence_slider = ttk.Scale(confidence_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL,
                                 value=confidence_values[template],
                                 command=lambda value, t=template, e=entry_var, s=slider_var: update_confidence(t, float(value), e, s))
    confidence_slider.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)

    # Create and configure an entry widget
    confidence_entry = Entry(confidence_frame, textvariable=entry_var, width=5)

    # Function to update confidence value when focus is lost
    def on_focus_out(event, template=template, entry_var=entry_var, slider_var=slider_var):
        try:
            value = float(entry_var.get())
            update_confidence(template, value, entry_var, slider_var)
        except ValueError:
            # Handle the case where the entered value is not a valid float
            entry_var.set(f"{confidence_values[template]:.2f}")  # Reset the entry to the previous value

    confidence_entry.bind("<FocusOut>", on_focus_out)

    # Function to update confidence value when Enter is pressed
    def on_enter(event, template=template, entry_var=entry_var, slider_var=slider_var):
        try:
            value = float(entry_var.get())
            update_confidence(template, value, entry_var, slider_var)
            confidence_slider.set(value)  # Update the slider with the entered value
        except ValueError:
            # Handle the case where the entered value is not a valid float
            entry_var.set(f"{confidence_values[template]:.2f}")  # Reset the entry to the previous value

        # Set focus to the root window to remove cursor from the entry box
        root.focus_set()

    confidence_entry.bind("<Return>", on_enter)

    confidence_entry.grid(row=row, column=2, pady=5, padx=5, sticky=tk.W)
    confidence_entries[template] = {'entry_var': entry_var, 'slider_var': confidence_slider}  # Update the entry and slider variables

    # Configure the "blue" tag for the "Looking for fish" color
    console_text.tag_configure("blue", foreground="blue", font=("TkDefaultFont", 10, "bold"))

# Function to update bait movement threshold
def update_bait_threshold(value):
    global bait_movement_threshold
    if bait_movement_threshold != value:
        bait_movement_threshold = value
        bait_threshold_var.set(f"{value:.2f}")
        log_output(f"Bait Movement Threshold: {value:.2f}", color="black", bold=True)

def on_threshold_focus_out(event):
    try:
        entered_value = float(bait_threshold_var.get())
        # Ensure the entered value is within the slider's range
        if bait_threshold_slider.cget("from") <= entered_value <= bait_threshold_slider.cget("to"):
            value = round(entered_value, 2)  # Round to two decimal places
            if value != bait_movement_threshold:
                update_bait_threshold(value)
                bait_threshold_slider.set(value)  # Update the corresponding slider
                bait_threshold_var.set(f"{value:.2f}")  # Set the rounded value to the entry
            else:
                # Value hasn't changed, no need to update or log
                return
        else:
            error_message = f"Invalid input. Please enter a value between {bait_threshold_slider.cget('from')} and {bait_threshold_slider.cget('to')}."
            log_output(error_message, color="red", bold=True)
            bait_threshold_var.set(f"{bait_movement_threshold:.2f}")  # Reset the entry to the previous value
    except (_tkinter.TclError, tk.TclError) as te:
        # Handle _tkinter.TclError (and also tk.TclError for additional compatibility)
        error_message = "Invalid input. Please enter a valid number for the threshold."
        log_output(error_message, color="red", bold=True)
        reset_value = f"{bait_movement_threshold:.2f}"  # Store the reset value
        bait_threshold_var.set(reset_value)  # Reset the entry to the previous value
        log_output(f"Reset to previous value: {reset_value}", color="black", bold=True)  # Log the reset value
    except ValueError as ve:
        # Handle the case where the entered value is not a valid float
        error_message = f"Invalid input. {str(ve)}"
        log_output(error_message, color="red", bold=True)
        reset_value = f"{bait_movement_threshold:.2f}"  # Store the reset value
        bait_threshold_var.set(reset_value)  # Reset the entry to the previous value
        log_output(f"Reset to previous value: {reset_value}", color="black", bold=True)  # Log the reset value
    except Exception as e:
        # Handle other exceptions
        error_message = f"An error occurred. {str(e)}"
        log_output(error_message, color="red", bold=True)
        reset_value = f"{bait_movement_threshold:.2f}"  # Store the reset value
        bait_threshold_var.set(reset_value)  # Reset the entry to the previous value
        log_output(f"Reset to previous value: {reset_value}", color="black", bold=True)  # Log the reset value


    # Set focus to the root window to remove the cursor from the entry box
    root.focus_set()

def on_threshold_enter(event):
    on_threshold_focus_out(event)
    # Set focus to the root window to remove cursor from the entry box
    root.focus_set()

# Function to toggle the "Keep in foreground" state
def toggle_keep_in_foreground():
    if keep_in_foreground_var.get() == 1:
        root.attributes("-topmost", True)  # Keep the main window in the foreground
    else:
        root.attributes("-topmost", False)  # Allow the main window to go behind other windows

# Function to toggle the "Human Reaction Time" state
def toggle_human_reaction_time():
    if human_reaction_time_var.get() == 1:
        # If checked, set a longer delay range
        delay_before_click_range = (1, 5)
    else:
        # If unchecked, set the original delay range
        delay_before_click_range = (1, 3)

    # Update the delay_before_click variable
    return random.uniform(*delay_before_click_range)


# Define a list of random actions
random_actions = [
    {'action': 'Open Bag', 'key': 'b', 'color': 'orange'},
    {'action': 'Open Map', 'key': 'm', 'color': 'blue'},
    {'action': 'Jump', 'key': 'space', 'color': 'purple'},
    {'action': 'Moving Left', 'key': 'q', 'color': 'red'},
    {'action': 'Moving Right', 'key': 'e', 'color': 'red'}
]

# Function to perform a random action
def perform_random_action():
    # Pick a random action from the list
    selected_action = random.choice(random_actions)

    # Log the action in the console with the specified color
    log_output(f"Performing Action: {selected_action['action']}", color=selected_action['color'])

    # Perform the selected action
    if selected_action['action'] == 'Open Bag' or selected_action['action'] == 'Open Map':
        pyautogui.press(selected_action['key'])
        time.sleep(random.uniform(2, 5))
        pyautogui.press(selected_action['key'])
    elif selected_action['action'] == 'Jump':
        pyautogui.press(selected_action['key'])
        time.sleep(random.uniform(2, 5))
    elif selected_action['action'] == 'Moving Left' or selected_action['action'] == 'Moving Right':
        # Press the key for 1-3 seconds
        pyautogui.keyDown(selected_action['key'])
        step_duration = random.uniform(1, 3)
        time.sleep(step_duration)
        pyautogui.keyUp(selected_action['key'])

        # Sleep for 1-3 seconds
        time.sleep(random.uniform(1, 3))

        # Move back to the original position by pressing the opposite key
        reverse_key = 'e' if selected_action['key'] == 'q' else 'q'
        pyautogui.keyDown(reverse_key)
        time.sleep(step_duration)
        pyautogui.keyUp(reverse_key)

# Function to toggle the state of random actions checkbox
def toggle_random_actions():
    if random_actions_checkbox_var.get() == 1:
        log_output("Random Actions enabled", color="black", bold=True)
    else:
        log_output("Random Actions disabled", color="black", bold=True)

# GUI setup with themed_tk
root = ThemedTk()
root.get_themes()  # Returns a list of available themes
root.set_theme("arc")  # Choose a theme from the available ones
root.title("Fishers Friend")
root.configure(bg='#22344f')  # Blue background
# Set the icon
root.iconbitmap(os.path.join(Path(__file__).resolve().parent, 'assets', 'fish_icon_2.ico'))

# Style adjustments for a more modern appearance
style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", font=("TkDefaultFont", 10))
style.configure("TLabel", font=("TkDefaultFont", 10), foreground='black')

# ScrolledText widget
console_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=15, bg='black', fg='white')  # Set text color to white
console_text.pack(pady=10)

# Tag configuration for colors
console_text.tag_configure("red", foreground="red", font=("TkDefaultFont", 10, "bold"))
console_text.tag_configure("green", foreground="green", font=("TkDefaultFont", 10, "bold"))
console_text.tag_configure("black", font=("TkDefaultFont", 10, "bold"))  # Remove foreground color for black tag
console_text.tag_configure("purple", foreground="purple", font=("TkDefaultFont", 10, "bold"))
console_text.tag_configure("orange", foreground="orange", font=("TkDefaultFont", 10, "bold"))  # Add new tag for orange color

# Confidence sliders and entry widgets
confidence_frame = ttk.Frame(root, style='TFrame', padding=(10, 10, 10, 10))  # Set style and padding
confidence_frame.pack(pady=10)

ttk.Label(confidence_frame, text="Confidence Levels:").grid(row=0, column=0, columnspan=4, pady=5, sticky=tk.W)

# Create sliders and entry widgets for each template
for i, template in enumerate(['Fishing Rod', 'Bait']):
    entry_var = tk.StringVar(value=f"{confidence_values[template]:.2f}")
    create_slider_and_entry(template, i + 1, entry_var, None)

# Threshold slider
threshold_frame = ttk.Frame(root, style='TFrame', padding=(10, 10, 10, 10))  # Set style and padding
threshold_frame.pack(pady=10)

ttk.Label(threshold_frame, text="Bait Movement Threshold:").grid(row=0, column=0, pady=5, sticky=tk.E)

# Create and configure a slider for the threshold
bait_threshold_slider = ttk.Scale(threshold_frame, from_=1, to=30, orient=tk.HORIZONTAL,
                                  value=bait_movement_threshold,
                                  command=lambda value: update_bait_threshold(float(value)))
bait_threshold_slider.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)

# Entry widget for Bait Movement Threshold
bait_threshold_var = tk.DoubleVar(value=bait_movement_threshold)
bait_threshold_entry = Entry(threshold_frame, textvariable=bait_threshold_var, width=5)

bait_threshold_entry.bind("<FocusOut>", on_threshold_focus_out)
bait_threshold_entry.bind("<Return>", on_threshold_enter)
bait_threshold_entry.grid(row=0, column=2, pady=5, padx=5, sticky=tk.W)

# Create a variable to hold the state of the "Keep in foreground" checkbox
keep_in_foreground_var = IntVar(value=0)

# Create a custom style for the checkbox with black text color
style = ttk.Style()
style.configure('BlackText.TCheckbutton', foreground='black')  # Set black text color

# Checkbox for "Keep in foreground" with the custom style
keep_in_foreground_checkbox = ttk.Checkbutton(
    root,
    text="Keep in Foreground",
    variable=keep_in_foreground_var,
    style='BlackText.TCheckbutton',  # Apply the custom style
    command=toggle_keep_in_foreground
)
keep_in_foreground_checkbox.pack(pady=5)


# Create a variable to hold the state of the "Human Reaction Time" checkbox
human_reaction_time_var = IntVar(value=0)

# Checkbox for "Human Reaction Time" with the custom style
human_reaction_time_checkbox = ttk.Checkbutton(
    root,
    text="Human Catch Rate (not 100%)",
    variable=human_reaction_time_var,
    style='BlackText.TCheckbutton',  # Apply the custom style
    command=toggle_human_reaction_time
)
human_reaction_time_checkbox.pack(pady=5)

# Create a variable to hold the state of the "Random Actions" checkbox
random_actions_checkbox_var = IntVar(value=0)

# Checkbox for "Random Actions" with the custom style
random_actions_checkbox = ttk.Checkbutton(
    root,
    text="Random Actions",
    variable=random_actions_checkbox_var,
    style='BlackText.TCheckbutton',  # Apply the custom style
    command=toggle_random_actions
)
random_actions_checkbox.pack(pady=5)

# Start/Stop buttons
button_frame = ttk.Frame(root, padding=(10, 10, 10, 10), style='TFrame')  # Set style and padding
button_frame.pack(pady=10)

# Create a new style for the buttons
button_style = ttk.Style()
button_style.configure('TButton', foreground='black')  # Set the text color to black

# Set Fishing Rod button
set_rod_button = ttk.Button(button_frame, text="Set Fishing Rod", command=lambda: set_image('Fishing Rod'))
set_rod_button.grid(row=0, column=0, padx=5, pady=5)

# Set Bait button
set_bait_button = ttk.Button(button_frame, text="Set Bait", command=lambda: set_image('Bait'))
set_bait_button.grid(row=0, column=1, padx=5, pady=5)

# Add some vertical space with a separator
ttk.Separator(button_frame, orient=tk.HORIZONTAL).grid(row=1, columnspan=2, sticky="ew", pady=5)


# Start button
start_button = ttk.Button(
    button_frame,
    text="Start",
    command=lambda: threading.Thread(target=execute_code).start(),
    style='Green.TButton'  # Set the custom style for the Start button
)
start_button.grid(row=2, column=0, padx=5, pady=5)

# Stop button
stop_button = ttk.Button(
    button_frame,
    text="Stop",
    command=stop_execution,
    style='Red.TButton'  # Set the custom style for the Stop button
)
stop_button.grid(row=2, column=1, padx=5, pady=5)

# Create a new style for the custom buttons
custom_button_style = ttk.Style()

# Configure the style for the Start button (green text)
custom_button_style.configure('Green.TButton', foreground='green')

# Configure the style for the Stop button (red text)
custom_button_style.configure('Red.TButton', foreground='red')


# Screenshot buttons
screenshot_frame = ttk.Frame(root, style='TFrame', padding=(10, 10, 10, 10))
screenshot_frame.pack(pady=10)

screenshot_label = ttk.Label(screenshot_frame, text="Screenshot will appear here", background='white')
screenshot_label.grid(row=0, column=0, columnspan=2, pady=5)

# Create a label for "Made by G33R0Y"
made_by_label = ttk.Label(root, text="Made by G33R0Y", font=("TkDefaultFont", 10), foreground='black')

# Display the starting message in the console
log_output(ascii_art, color="blue", initial_message=True)

root.mainloop()
# Fishers Friend

Fishers Friend is an automation script designed to assist players in performing various actions in a fishing game. The script utilizes the `pyautogui` library to simulate keyboard presses and the `Tkinter` library for the graphical user interface (GUI). The main features include setting confidence levels, adjusting bait movement thresholds, enabling random actions, and providing visual feedback through a console.

## Features

### Confidence Levels
The script allows users to set confidence levels for different in-game actions such as using the fishing rod or bait. The confidence levels are adjustable through sliders and entry widgets in the GUI.

### Bait Movement Threshold
Users can set a threshold for detecting bait movement. The threshold can be adjusted using a slider or by entering a specific value in the corresponding entry widget.

### Keep in Foreground
The "Keep in Foreground" checkbox allows the user to toggle whether the main window should stay on top of other windows.

### Human Reaction Time
The "Human Catch Rate" checkbox introduces variability in the delay before certain actions, simulating a more human-like reaction time.

### Random Actions
Enabling the "Random Actions" checkbox triggers the script to perform random in-game actions, such as opening the bag, map, jumping, or moving left and right.


## Dependencies
### GUI library
- `tk`
### Additional GUI components
- `ttkthemes`
- `Pillow`
### Utility libraries
- `pyautogui`
- `numpy`
- `pytweening`
- `opencv-python`

## Installation & How to Run

1. Ensure Python is installed on your system.
2. Download the Repository
3. Unzip Folder and switch into the created 'FishersFriend' folder
4. Open a Terminal(cmd) in the 'FishersFriend' folder and run:
   ```
   pip install -r requirements.txt
   ```
5. Now you can double-click the FishersFriend.py or run it from your IDE


## Usage
1. **Set Fishing Rod:**
   - If clicked a Screenshot gets taken and you can mark the Icon of the Fishing Rod in the taken Screenshot and confirm it to set it as the Image which should be found.
2. **Set Bait:**
   - If clicked a Screenshot gets taken and you can mark the the Bait (recommending only the inside of the feathers) in the taken Screenshot and confirm it to set it as the Image which should be found.

     Bait Example:

     ![Bait Example](images/bait_example.PNG)

1. **Set Confidence Levels:**
   - Adjust confidence levels for the fishing rod and bait image recognition using the provided sliders or entry widgets.
   (Recommending to start with default and adjust if needed)

2. **Set Bait Movement Threshold:**
   - Set the threshold for bait movement using the slider or enter a specific value.

3. **Keep in Foreground:**
   - Toggle the "Keep in Foreground" checkbox based on the user's preference.

4. **Human Reaction Time:**
   - Toggle the "Human Catch Rate" checkbox to introduce variability in reaction times.

5. **Random Actions:**
   - Enable the "Random Actions" checkbox to perform random in-game actions periodically.

6. **Start/Stop:**
   - Click the "Start" button to begin the script execution, and use the "Stop" button to halt the execution.

7. **Set Fishing Rod/Bait:**
   - Use the "Set Fishing Rod" and "Set Bait" buttons to set images for the corresponding in-game actions.





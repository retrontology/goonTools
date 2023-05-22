import mido
from pynput import keyboard
from threading import Thread
from time import sleep

KEYMAP="1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm"
MIDI_PORT='loopMIDI Port 0'
MIDDLE_C_OFFSET=36

#KEYMAP="eErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCv"
#MIDDLE_C_OFFSET=57

def map_note_to_key(note, keymap=KEYMAP, offset=MIDDLE_C_OFFSET):
    index = note - offset
    if index > 0 and index < len(keymap):
        return keymap[index]
    else:
        return None
    
def map_message_to_key(message):
    note_off = False
    if message.type == 'note_on':
        if message.velocity == 0:
            note_off = True
        else:
            key = map_note_to_key(message.note, KEYMAP)
            if key:
                kb_controller.press(key)
    if message.type == 'note_off' or note_off:
        key = map_note_to_key(message.note, KEYMAP)
        if key:
            kb_controller.release(key)

def play_midi_file(file):
    midi_file = mido.MidiFile(file, clip=True)
    for message in midi_file.play():
        map_message_to_key(message)

def capture_input_port(name=None):
    inport = mido.open_input(name, callback=map_message_to_key)
    while True:
        sleep(60)

def main():
    # for i in range(10):
    #     print(10-i)
    #     sleep(1)
    # play_midi_file('Sea_Shanty_2.mid')
    capture_input_port(MIDI_PORT)

if __name__ == "__main__":
    kb_controller = keyboard.Controller()
    main()
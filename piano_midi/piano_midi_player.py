import mido
from pynput import keyboard
from time import sleep
import argparse
from functools import partial
import pytemidi


KEYMAP="1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm"
MIDDLE_C_OFFSET=36
INTERNAL_DEVICE_NAME='GoonMidi'

def parse_args():
    parser = argparse.ArgumentParser(
        prog='piano_midi_player',
        description='A program that listens to a MIDI device for events and maps them to keybinds for Goonstation instruments'
    )
    parser.add_argument(
        '-d', '--device',
        default=None,
        help=f'The MIDI device you want to listen to. If left blank a device will be created.'
    )
    parser.add_argument(
        '-o', '--offset',
        default=MIDDLE_C_OFFSET,
        help=f'The middle C offset (default is {MIDDLE_C_OFFSET})'
    )
    parser.add_argument(
        '-k', '--keymap',
        default=KEYMAP,
        help=f'The string of keys to map'
    )
    return parser.parse_args()

def map_note_to_key(note, keymap, offset):
    index = note - offset
    if index > 0 and index < len(keymap):
        return keymap[index]
    else:
        return None
    
def map_message_to_key(message, keymap, offset):
    note_off = False
    if message.type == 'note_on':
        if message.velocity == 0:
            note_off = True
        else:
            key = map_note_to_key(message.note, keymap, offset)
            if key:
                kb_controller.press(key)
    if message.type == 'note_off' or note_off:
        key = map_note_to_key(message.note, keymap, offset)
        if key:
            kb_controller.release(key)

def play_midi_file(file):
    midi_file = mido.MidiFile(file, clip=True)
    for message in midi_file.play():
        map_message_to_key(message)

def capture_input_port(name, keymap, offset):
    map_func = partial(map_message_to_key, keymap=keymap, offset=offset)
    inport = mido.open_input(name, callback=map_func)
    print(f'The midi mapper is now listening to {name}. Either close this window or type Ctrl+C to exit...')
    try:
        while True:
            sleep(60)
    except KeyboardInterrupt as e:
        print('Goodbye!')
        
def get_full_device_name(devices, target):
    for i in range(len(devices)):
        if target == devices[i][0:-len(f' i')]:
            return devices[i]
    else:
        return None

def main():
    args = parse_args()
    if args.device == None:
        own_device = True
        loopback = pytemidi.Device(INTERNAL_DEVICE_NAME)
        loopback.create()
        device = INTERNAL_DEVICE_NAME
    else:
        own_device = False
        device = args.device
    full_device = get_full_device_name(mido.get_input_names(), device)
    if not full_device:
        raise(Exception("Could not find MIDI device: {device}"))
    capture_input_port(full_device, args.keymap, args.offset)

if __name__ == "__main__":
    kb_controller = keyboard.Controller()
    main()
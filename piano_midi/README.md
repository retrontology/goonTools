## piano_midi
### Description
This is a simple script that listens to a specified MIDI port and translates notes to keybind for the instruments in Goonstation SS13. This is not something that can be used as a standalone. You'll either need a MIDI device connected to your computer in order to play live music or a software based MIDI player. For the latter, I personally use [Midi Player](https://falcosoft.hu/softwares.html#midiplayer). If you use a software based MIDI player, you'll also need to install [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html). You don't actually need to use the software, the script requires drivers that are installed alongside [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html).
Note: the piano window needs to be in focus/the last window you clicked on in order for the keybinds to work.

### Installation
Install the requirements with the following command:
```
python -m pip install --upgrade -r requirements.txt
```

### Usage
```
piano_midi_player [-h] [-d DEVICE] [-o OFFSET] [-k KEYMAP]

options:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        The MIDI device you want to listen to. If left blank a device will be created.
  -o OFFSET, --offset OFFSET
                        The middle C offset (default is 36)
  -k KEYMAP, --keymap KEYMAP
                        The string of keys to map
```

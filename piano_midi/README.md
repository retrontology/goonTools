## piano_midi
### Description
This is a simple script that listens to a specified MIDI port and translates notes to keybind for the instruments in Goonstation SS13. This is not something that can be used as a standalone. You'll either need a MIDI device connected to your computer in order to play live music or a virtual MIDI loopback device in conjuction with a MIDI player. For the latter, I personally use [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) and [Midi Player](https://falcosoft.hu/softwares.html#midiplayer) for the latter.
Note: the piano window needs to be in focus/the last window you clicked on in order for the keybinds to work.

### Installation
Install the requirements with the following command:
```
python -m pip install -r requirements.txt
```

### Usage
Change the `MIDI_PORT' constanst in the script to the name of the MIDI device you wish to listen to. If you're using [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) the script should already be set to the default device name

Run the script with the following command:
```
python piano_midi_player.py
```
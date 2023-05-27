# goonTools
### Description
Collection of Python scripts I developed to use with the Goonstation codebase of SS13. These tools are split into their own dedicated root directory:

------

## piano_midi
### Description
This is a simple script that listens to a specified MIDI port and translates notes to keybind for the instruments in Goonstation SS13. This is not something that can be used as a standalone. You'll either need a MIDI device connected to your computer in order to play live music or a virtual MIDI loopback device in conjuction with a MIDI player. For the latter, I personally use [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) and [Midi Player](https://falcosoft.hu/softwares.html#midiplayer) for the latter.
Note: the piano window needs to be in focus/the last window you clicked on in order for the keybinds to work.

------

## harmonic_siphon
### Description
This is a Harmonic Siphon simulator written in `pygame`. It allows for prototyping designs for the Harmonic Siphon as well as saving and loading those designs.
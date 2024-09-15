import sys
import random
import fluidsynth
from midiutil import MIDIFile

"""
Takes a text guitar tab input, and changes the music to a different key with a different melody.
This is my attempt at writing a script to perform algorithmic musical composition.
"""

def get_scale(roots, steps):
    """
    Returns a 2D list of each note on each string that is in a specific key.

    Arguments:
    roots: A list of root notes of the scale corresponding to where this note is on each string
    steps: The order in which the scale steps (whole steps and half steps)
    """
    scale = []
    for note in roots:
        scale.append([note])

    for string in scale:
        num = string[0]
        while num <= 24:
            for step in steps:
                num += step
                if num > 24:
                    break
                string.append(num)

    for string in scale:
        num = string[0]
        while num >= 0:
            for step in steps[::-1]:
                num -= step
                if num < 0:
                    break
                string.insert(0, num)

    return scale

def get_scale_steps(name_of_scale):
    """
    Returns a list of the steps in the given scale.
    """
    scales = {
        "minor": [2, 1, 2, 2, 1, 2, 2],
        "major": [2, 2, 1, 2, 2, 2, 1],
        "harmonic": [2, 1, 2, 2, 1, 3, 1],
        "dorian": [2, 1, 2, 2, 2, 1, 2],
        "mixolydian": [2, 2, 1, 2, 2, 1, 2],
        "pentatonic": [3, 2, 2, 3, 2]
    }
    return scales[name_of_scale]

def get_root_note_positions(root, instrument="guitar", tuning="standard"):
    """
    Returns the root note positions for the specified instrument and tuning.
    """
    tunings = {
        "guitar": {
            "standard": [40, 45, 50, 55, 59, 64],
            "drop_d": [38, 45, 50, 55, 59, 64],
            "half_step_down": [39, 44, 49, 54, 58, 63]
        },
        "bass_4_string": {
            "standard": [40, 45, 50, 55],
            "drop_d": [38, 45, 50, 55],
            "half_step_down": [39, 44, 49, 54]
        },
        "bass_5_string": {
            "standard": [35, 40, 45, 50, 55]
        }
    }
    return tunings[instrument][tuning]


def strip_empty_lines(string):
    """
    Removes empty lines from the input string.
    """
    final_str = ""
    for line in string.split('\n'):
        if not line.isspace() and len(line) > 0:
            final_str += line + '\n'
    return """%s """ % final_str

def print_scale(scale):
    """
    Prints a representation of the neck of the guitar for this specific scale.
    """
    for i in scale:
        print(i)

def change_key(note, scale, string, accidental=-1):
    """
    Changes the key of a note based on the scale.
    """
    random_offset = 0
    min_fret = min(scale[string], key=lambda fret: abs(fret - note))

    if accidental > 0:
        rand_num = random.randrange(0, accidental, 1)
        random_offset = 1 if rand_num == 1 else -1

    return min_fret + random_offset

def go_through_file(song, scale, method, accidental=-1, instrument="guitar"):
    """
    Processes the tab file and applies the selected operation (e.g., change key).
    """
    modified_song = ""
    string = 5 if instrument == "guitar" else 3
    previous_note = '-'
    song = strip_empty_lines(song)

    for note in song:
        if string < 0:
            modified_song += '\n'
            string = 5 if instrument == "guitar" else 3

        if note.isdigit():
            if previous_note.isdigit():
                note = previous_note + note
                note = int(note)
                previous_note = '-'
                if method == 'ck':
                    str_to_add = str(change_key(note, scale, string, accidental))
                    if len(str_to_add) > 1:
                        modified_song += str_to_add
                    else:
                        modified_song += str_to_add + '-'
            else:
                previous_note = note
        else:
            if previous_note.isdigit():
                non_note_char = note
                note = int(previous_note)
                previous_note = '-'
                if method == 'ck':
                    modified_song += str(change_key(note, scale, string, accidental)) + non_note_char
            else:
                if note != '\n':
                    modified_song += note
        if note == '\n':
            previous_note = '-'
            modified_song += '\n'
            string -= 1

    if previous_note.isdigit():
        if method == 'ck':
            modified_song += str(change_key(int(previous_note), scale, string, accidental))

    return modified_song

def fret_to_midi_note_string(string, fret, instrument="guitar"):
    """
    Converts string and fret information to a MIDI note number.
    """
    guitar_open_strings = [40, 45, 50, 55, 59, 64]  # Standard guitar tuning (EADGBE)
    bass_open_strings = [40, 45, 50, 55]  # Standard 4-string bass tuning (EADG)
    bass_5_open_strings = [35, 40, 45, 50, 55]  # 5-string bass tuning (BEADG)

    if instrument == "guitar":
        return guitar_open_strings[string] + fret
    elif instrument == "bass_4_string":
        if 0 <= string < len(bass_open_strings):  # Prevent out-of-range errors
            return bass_open_strings[string] + fret
        else:
            raise IndexError("String index out of range for 4-string bass")
    elif instrument == "bass_5_string":
        if 0 <= string < len(bass_5_open_strings):  # Prevent out-of-range errors
            return bass_5_open_strings[string] + fret
        else:
            raise IndexError("String index out of range for 5-string bass")


def tab_to_midi(tab, instrument="guitar"):
    """
    Converts a guitar or bass tab to a MIDI file.
    """
    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTrackName(track, time, "Riff")
    midi.addTempo(track, time, 120)

    channel = 0
    duration = 1
    velocity = 100

    # Set the number of strings based on the instrument
    if instrument == "guitar":
        string_count = 6  # 6 strings for guitar
    elif instrument == "bass_4_string":
        string_count = 4  # 4 strings for 4-string bass
    elif instrument == "bass_5_string":
        string_count = 5  # 5 strings for 5-string bass

    # Iterate over each line in the tab
    for line in tab.split('\n'):
        string = string_count - 1  # Start with the lowest string
        for char in line:
            if char.isdigit():
                fret = int(char)
                if string >= 0:
                    midi_note = fret_to_midi_note_string(string, fret, instrument)
                    midi.addNote(track, channel, midi_note, time, duration, velocity)
            elif char == '\n':
                time += 1
            string -= 1  # Move to the next string up, but ensure it doesn't go below 0

    return midi


def save_midi_to_file(midi, filename):
    """
    Saves the generated MIDI object to a file.
    """
    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)

def midi_to_wav(midi_filename, wav_filename):
    """
    Converts a MIDI file to a WAV file using FluidSynth.
    """
    fs = fluidsynth.Synth()
    soundfont_path = "soundfonts/GeneralUser_GS.sf2"  # Path to your SoundFont file
    sfid = fs.sfload(soundfont_path)  # Load the SoundFont file
    fs.program_select(0, sfid, 0, 0)  # Select the program (instrument)

    fs.midi_file_play(midi_filename)
    fs.write_wave(os.path.join("static", wav_filename))  # Save the WAV file in the static folder
    fs.delete()
def translate_guitar_to_bass(guitar_tab, guitar_scale, bass_scale):
    """
    Translates a guitar tab to a bass tab by adjusting notes to the bass scale.
    
    Arguments:
    guitar_tab: The original guitar tab as a string.
    guitar_scale: The scale for the guitar.
    bass_scale: The scale for the bass.
    
    Returns:
    A string representing the bass tab.
    """
    bass_tab = ""
    string = 3  # For bass, we only have 4 strings (0-3), 4-string bass
    previous_note = '-'
    guitar_tab = strip_empty_lines(guitar_tab)

    for note in guitar_tab:
        if string < 0:
            bass_tab += '\n'
            string = 3  # Reset to the highest bass string (4-string bass)

        if note.isdigit():
            if previous_note.isdigit():
                note = previous_note + note
                note = int(note)
                previous_note = '-'
                # Find the closest note in the bass scale
                closest_note = min(bass_scale[string], key=lambda x: abs(x - note))
                bass_tab += str(closest_note) + '-'
            else:
                previous_note = note
        else:
            if previous_note.isdigit():
                bass_tab += note
                previous_note = '-'
            else:
                bass_tab += note

        if note == '\n':
            previous_note = '-'
            string -= 1

    return bass_tab


import random
from midiutil import MIDIFile

"""
Core music helpers for RiffEdit.

This module owns the non-UI music logic: simple scale construction, legacy
tab transformations, text-tab parsing, MIDI export, and guitar-to-bass mapping.
Most functions are intentionally small so the Flask routes and browser UI can
share the same parsing contract.
"""

def get_scale(roots, steps):
    """
    Build allowed fret numbers for each string in a scale.

    Arguments:
    roots: Starting fret numbers, one per string.
    steps: Semitone movement pattern for the scale.

    Returns:
    A list where each inner list contains fret numbers that belong to the scale
    for that string. These fret numbers are used by change_key() to snap input
    notes onto the selected scale.
    """
    scale = []
    for note in roots:
        scale.append([note])

    # Walk upward from each starting point until the playable 24-fret range ends.
    for string in scale:
        num = string[0]
        while num <= 24:
            for step in steps:
                num += step
                if num > 24:
                    break
                string.append(num)

    # Walk backward as well so open-position notes can be mapped into the scale.
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
    Return semitone intervals for the named scale or mode.

    The UI only sends keys that exist in this dictionary, so a KeyError here is
    useful during development because it reveals a mismatched option value.
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
    Return open-string MIDI notes for the selected instrument and tuning.

    Note: the root argument is retained for compatibility with the original
    API, but this function currently returns tuning positions rather than true
    root-note fret positions. A future theory pass could use root to choose
    root-aware scale anchors.
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
            "standard": [35, 40, 45, 50, 55],
            "drop_d": [35, 38, 45, 50, 55],
            "half_step_down": [34, 39, 44, 49, 54]
        }
    }
    return tunings[instrument][tuning]


def strip_empty_lines(string):
    """
    Remove blank lines before legacy character-by-character tab transforms.

    The trailing space preserves the original parser's behavior, which expects a
    non-newline character after the last line when it flushes pending notes.
    """
    final_str = ""
    for line in string.split('\n'):
        if not line.isspace() and len(line) > 0:
            final_str += line + '\n'
    return """%s """ % final_str

def print_scale(scale):
    """
    Development helper that prints the generated scale map for each string.
    """
    for i in scale:
        print(i)

def change_key(note, scale, string, accidental=-1):
    """
    Snap a fret number to the nearest allowed fret in the selected scale.

    accidental controls the legacy "add randomness" mode by nudging some mapped
    notes up or down one fret after the nearest scale tone is selected.
    """
    random_offset = 0
    min_fret = min(scale[string], key=lambda fret: abs(fret - note))

    if accidental > 0:
        rand_num = random.randrange(0, accidental, 1)
        random_offset = 1 if rand_num == 1 else -1

    return min_fret + random_offset

def go_through_file(song, scale, method, accidental=-1, instrument="guitar"):
    """
    Legacy text-tab transformer used by the Change Key operations.

    This parser walks the submitted tab one character at a time, assumes rows are
    ordered from high string to low string, and preserves non-note characters so
    spacing remains close to the user's original tab. New playback/export code
    uses tab_to_note_events() instead because it has a clearer data contract.
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
    Convert a low-to-high string index plus fret number into a MIDI note.

    Open-string arrays are ordered lowest string first. extract_tab_lines()
    returns visual tab rows highest string first, so tab_to_note_events() flips
    the row index before calling this function.
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


def get_string_count(instrument="guitar"):
    """
    Return the number of tab rows expected for the selected instrument.
    """
    if instrument == "guitar":
        return 6
    if instrument == "bass_4_string":
        return 4
    if instrument == "bass_5_string":
        return 5
    raise ValueError(f"Unsupported instrument: {instrument}")


def extract_tab_lines(tab, instrument="guitar"):
    """
    Extract playable tab rows from raw pasted text.

    Optional string labels such as "e|" or "G|" are stripped because playback
    only needs the timeline characters after the first bar. Rows are expected
    highest string to lowest string, matching common guitar and bass tabs.
    """
    string_count = get_string_count(instrument)
    tab_lines = []

    for raw_line in tab.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if "|" in line:
            line = line.split("|", 1)[1]

        if any(char.isdigit() for char in line):
            tab_lines.append(line)

    return tab_lines[:string_count]


def tab_to_note_events(tab, instrument="guitar", step_duration=0.25, note_duration=0.22):
    """
    Convert text tablature into the shared note-event contract.

    Each event contains:
    midi: MIDI note number.
    time: Start time in seconds at the default 120 BPM grid.
    duration: Intended note length in seconds before tempo scaling.
    line/column: Visual tab coordinates used by the browser highlighter.
    fret: Display text for the note, including multi-digit frets or "x".
    technique: Lightweight marker for hammer-ons, slides, bends, vibrato, etc.
    muted: True for "x" hits, which playback renders as percussive thunks.
    """
    tab_lines = extract_tab_lines(tab, instrument)
    string_count = get_string_count(instrument)
    events = []

    for line_index, line in enumerate(tab_lines):
        string = string_count - 1 - line_index
        column = 0

        while column < len(line):
            if line[column].isdigit():
                start_column = column
                fret_text = ""

                # Consecutive digits are one fret value, so "12" is fret twelve
                # rather than two separate notes at the same tab position.
                while column < len(line) and line[column].isdigit():
                    fret_text += line[column]
                    column += 1

                fret = int(fret_text)
                events.append({
                    "midi": fret_to_midi_note_string(string, fret, instrument),
                    "time": round(start_column * step_duration, 3),
                    "duration": note_duration,
                    "line": line_index,
                    "column": start_column,
                    "fret": fret_text,
                    # Store a nearby technique marker for future playback and
                    # notation work without changing the current timing model.
                    "technique": line[column] if column < len(line) and line[column] in "hHpP/\\bB~" else "",
                    "muted": False,
                })
            elif line[column].lower() == "x":
                # Muted notes are still timed events so the preview can show and
                # play rhythmic dead notes instead of silently skipping them.
                events.append({
                    "midi": fret_to_midi_note_string(string, 0, instrument),
                    "time": round(column * step_duration, 3),
                    "duration": min(note_duration, 0.12),
                    "line": line_index,
                    "column": column,
                    "fret": "x",
                    "technique": "mute",
                    "muted": True,
                })
                column += 1
            else:
                column += 1

    return sorted(events, key=lambda event: event["time"])


def tab_to_midi(tab, instrument="guitar", step_duration=0.25, note_duration=0.22):
    """
    Convert parsed guitar or bass tab events into a one-track MIDI file.

    MIDI export intentionally consumes tab_to_note_events() so browser preview
    and downloaded MIDI agree on pitch and timing.
    """
    midi = MIDIFile(1)
    track = 0
    time = 0
    midi.addTrackName(track, time, "Riff")
    midi.addTempo(track, time, 120)

    channel = 0
    duration = 1
    velocity = 100

    for event in tab_to_note_events(tab, instrument, step_duration, note_duration):
        midi.addNote(
            track,
            channel,
            event["midi"],
            event["time"],
            max(event["duration"], duration * 0.25),
            55 if event.get("muted") else velocity,
        )

    return midi


def save_midi_to_file(midi, filename):
    """
    Persist a MIDIFile object for Flask's send_file download response.
    """
    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)

def translate_guitar_to_bass(guitar_tab, guitar_scale, bass_scale):
    """
    Create a simple 4-string bass interpretation of a guitar tab.
    
    Arguments:
    guitar_tab: The original guitar tab as a string.
    guitar_scale: The scale for the guitar. Kept for API compatibility.
    bass_scale: The scale for the bass.
    
    Returns:
    A string representing the bass tab.

    This is a first-pass arranger, not a full musical transcription engine: it
    maps encountered fret numbers to the closest available note on the current
    bass string while preserving the rough text rhythm of the original tab.
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


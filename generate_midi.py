from midiutil import MIDIFile

# Create a MIDI object
midi = MIDIFile(1)  # One track
track = 0  # Track number
time = 0  # Start at the beginning
midi.addTrackName(track, time, "Sample Track")
midi.addTempo(track, time, 120)  # Set the tempo to 120 BPM

# Add a note (C4)
channel = 0
pitch = 60  # MIDI note number for C4
duration = 1  # Duration of 1 beat
volume = 100  # Volume (0-127)
midi.addNote(track, channel, pitch, time, duration, volume)

# Add more notes to create a simple melody
notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C4 to C5 scale

for i, note in enumerate(notes):
    midi.addNote(track, channel, note, time + i, duration, volume)

# Save the MIDI file
with open("sample_midi.mid", "wb") as output_file:
    midi.writeFile(output_file)

print("MIDI file generated: sample_midi.mid")

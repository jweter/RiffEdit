from flask import Flask, render_template, request, redirect, send_file, url_for
from Algcomposer import *
import os

app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template('index.html')

@app.route('/submit', methods=['POST', 'GET'])
def perform_script():
    # Initialize variables
    output = ""
    option = request.form["options"]
    root = request.form["root"]
    scale = request.form["scale"]
    song = """%s""" % request.form["guitar_tab"]

    # New inputs for instrument and tuning
    instrument = request.form["instrument"]
    tuning = request.form["tuning"]

    # Initialize the scale chosen by the user
    steps = get_scale_steps(scale)
    root_positions_guitar = get_root_note_positions(root, "guitar", "standard")  # For guitar
    root_positions_bass = get_root_note_positions(root, instrument, tuning)  # For bass


    guitar_scale = get_scale(root_positions_guitar, steps)
    bass_scale = get_scale(root_positions_bass, steps)

    # Execute the method chosen by the user
    if option == 'ck':
        output = go_through_file(song, get_scale(root_positions_guitar, steps), option, instrument="guitar")
    if option == 'ckr':
        output = go_through_file(song, get_scale(root_positions_guitar, steps), 'ck', 5, instrument="guitar")

    # Translate guitar riff to bass riff
    if instrument == "bass_4_string":
        bass_riff = translate_guitar_to_bass(song, guitar_scale, bass_scale)
        output += "\n\nBass Tab (4-string):\n" + bass_riff

    # Render the result in submitted.html and pass the output back to the page
    return render_template('submitted.html', output=output, song=song, option=option, root=root, scale=scale, instrument=instrument, tuning=tuning)

@app.route('/play_midi', methods=['POST'])
def play_midi():
    song = request.form["guitar_tab"]
    instrument = request.form["instrument"]

    # Convert the tab to MIDI
    midi = tab_to_midi(song, instrument)
    midi_filename = "generated_riff.mid"
    save_midi_to_file(midi, midi_filename)

    # Convert the MIDI file to WAV for playback
    wav_filename = "generated_riff.wav"
    midi_to_wav(midi_filename, wav_filename)

    # Serve the WAV file for playback
    return render_template('play_midi.html', wav_filename=wav_filename)

@app.route('/download_midi', methods=['POST'])
def download_midi():
    song = request.form["guitar_tab"]
    instrument = request.form["instrument"]

    # Convert the tab to MIDI
    midi = tab_to_midi(song, instrument)

    # Save the MIDI to a file
    midi_filename = "generated_riff.mid"
    save_midi_to_file(midi, midi_filename)

    # Send the file to the user for download
    return send_file(midi_filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

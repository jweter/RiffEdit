import json

from flask import Flask, Response, jsonify, render_template, request, redirect, send_file, url_for
from Algcomposer import *
import os

app = Flask(__name__)

# Separator used by the legacy transform flow when it appends a generated bass
# interpretation beneath the transformed guitar tab.
BASS_TAB_MARKER = "\n\nBass Tab (4-string):\n"

@app.route('/')
def main_page():
    """Render the modern single-page workbench."""
    return render_template('index.html')

def transform_riff(song, option, root, scale, instrument, tuning):
    """
    Apply the selected musical transform and choose the tab that should be
    previewed/exported.

    Returns:
        output: Full text shown to the user in the Transform tab.
        preview_tab: The specific tab used for playback/export. For generated
            4-string bass parts, this is the bass-only section.
    """
    output = ""
    steps = get_scale_steps(scale)

    # The current transform logic changes notes against a guitar scale first,
    # then optionally maps that transformed idea into bass space.
    root_positions_guitar = get_root_note_positions(root, "guitar", "standard")
    root_positions_bass = get_root_note_positions(root, instrument, tuning)

    guitar_scale = get_scale(root_positions_guitar, steps)
    bass_scale = get_scale(root_positions_bass, steps)

    if option == 'ck':
        output = go_through_file(song, guitar_scale, option, instrument="guitar")
    if option == 'ckr':
        output = go_through_file(song, guitar_scale, 'ck', 5, instrument="guitar")

    if instrument == "bass_4_string":
        bass_riff = translate_guitar_to_bass(song, guitar_scale, bass_scale)
        output += BASS_TAB_MARKER + bass_riff

    # Playback should focus on the instrument the user selected. When the
    # transform produces an appended bass section, use that section for preview.
    preview_tab = output
    if instrument == "bass_4_string" and BASS_TAB_MARKER in output:
        preview_tab = output.split(BASS_TAB_MARKER, 1)[1]

    # Some older transform paths can produce unplayable text for bass input.
    # Falling back to the submitted tab keeps preview/export useful instead of
    # returning a silent workbench.
    if not tab_to_note_events(preview_tab, instrument) and tab_to_note_events(song, instrument):
        preview_tab = song

    return output, preview_tab

def get_timing_values(data):
    """Normalize timing values from either JSON payloads or submitted forms."""
    step_duration = float(data.get("step_duration", 0.25))
    note_duration = float(data.get("note_duration", 0.22))
    return step_duration, note_duration

def tab_to_musicxml(tab, instrument, step_duration=0.25, note_duration=0.22):
    """
    Export a simple MusicXML score from parsed tab events.

    This is intentionally conservative: it emits pitch events in a single
    measure so notation programs have a valid import target. Richer measure
    grouping, rests, ties, and string/fret technique markup can build on this.
    """
    events = tab_to_note_events(tab, instrument, step_duration, note_duration)
    pitch_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    notes = []

    for event in events:
        midi = event["midi"]
        pitch = pitch_names[midi % 12]
        octave = midi // 12 - 1
        alter = ""
        step = pitch[0]
        if len(pitch) > 1:
            alter = "<alter>1</alter>"
        notes.append(f"""
        <note>
          <pitch><step>{step}</step>{alter}<octave>{octave}</octave></pitch>
          <duration>1</duration>
          <type>16th</type>
        </note>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1"><part-name>RiffEdit {instrument}</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <key><fifths>0</fifths></key>
        <time><beats>4</beats><beat-type>4</beat-type></time>
        <clef><sign>TAB</sign><line>5</line></clef>
      </attributes>
      {''.join(notes)}
    </measure>
  </part>
</score-partwise>
"""

@app.route('/api/transform', methods=['POST'])
def api_transform():
    """JSON endpoint used by the single-page workbench."""
    data = request.get_json(force=True)
    song = data.get("guitar_tab", "")
    instrument = data.get("instrument", "guitar")
    step_duration, note_duration = get_timing_values(data)
    output, preview_tab = transform_riff(
        song=song,
        option=data.get("options", "ck"),
        root=data.get("root", "a"),
        scale=data.get("scale", "minor"),
        instrument=instrument,
        tuning=data.get("tuning", "standard"),
    )
    note_events = tab_to_note_events(preview_tab, instrument, step_duration, note_duration)
    return jsonify({
        # Full transformed text and the playback/export-ready tab are both
        # returned so the UI can show all context while playing the right part.
        "output": output,
        "preview_tab": preview_tab,
        "tab_lines": extract_tab_lines(preview_tab, instrument),
        "note_events": note_events,
        "instrument": instrument,
    })

@app.route('/submit', methods=['POST', 'GET'])
def perform_script():
    """Legacy multi-page form endpoint kept as a fallback."""
    option = request.form["options"]
    root = request.form["root"]
    scale = request.form["scale"]
    song = """%s""" % request.form["guitar_tab"]
    instrument = request.form["instrument"]
    tuning = request.form["tuning"]
    output, preview_tab = transform_riff(song, option, root, scale, instrument, tuning)

    # Render the result in submitted.html and pass the output back to the page
    return render_template('submitted.html', output=output, preview_tab=preview_tab, song=song, option=option, root=root, scale=scale, instrument=instrument, tuning=tuning)

@app.route('/play_audio', methods=['POST'])
@app.route('/play_midi', methods=['POST'])
def play_audio():
    """Legacy audio preview page kept for compatibility with older links."""
    song = request.form.get("preview_tab") or request.form["guitar_tab"]
    instrument = request.form["instrument"]
    tab_lines = extract_tab_lines(song, instrument)

    step_duration, note_duration = get_timing_values(request.form)
    note_events = tab_to_note_events(song, instrument, step_duration, note_duration)
    if not note_events:
        return render_template(
            'play_midi.html',
            notes_json="[]",
            tab_lines_json=json.dumps(tab_lines),
            tab_text=song,
            tab_text_json=json.dumps(song),
            instrument=instrument,
            error_message="No playable notes were found in the submitted tab.",
        )

    return render_template(
        'play_midi.html',
        notes_json=json.dumps(note_events),
        tab_lines_json=json.dumps(tab_lines),
        tab_text=song,
        tab_text_json=json.dumps(song),
        instrument=instrument,
        error_message=None,
    )

@app.route('/download_midi', methods=['POST'])
def download_midi():
    """Create a MIDI file from the current preview tab and send it to browser."""
    song = request.form.get("preview_tab") or request.form["guitar_tab"]
    instrument = request.form["instrument"]

    # Convert the tab to MIDI
    step_duration, note_duration = get_timing_values(request.form)
    midi = tab_to_midi(song, instrument, step_duration, note_duration)

    # Save the MIDI to a file
    midi_filename = "generated_riff.mid"
    save_midi_to_file(midi, midi_filename)

    # Send the file to the user for download
    return send_file(midi_filename, as_attachment=True)

@app.route('/download_musicxml', methods=['POST'])
def download_musicxml():
    """Create a simple MusicXML file from the current preview tab."""
    song = request.form.get("preview_tab") or request.form["guitar_tab"]
    instrument = request.form["instrument"]
    step_duration, note_duration = get_timing_values(request.form)
    xml = tab_to_musicxml(song, instrument, step_duration, note_duration)
    return Response(
        xml,
        mimetype="application/vnd.recordare.musicxml+xml",
        headers={"Content-Disposition": "attachment; filename=riffedit.musicxml"},
    )

if __name__ == '__main__':
    # Heroku-style deployments may provide PORT; local development defaults to
    # Flask's familiar 5000.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

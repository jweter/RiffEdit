# RiffEdit

RiffEdit is a Flask web app for experimenting with text-based guitar and bass tablature. It can transpose riffs, add controlled randomness, translate guitar ideas to bass, preview clean guitar/bass audio in the browser, and export tab, MIDI, or MusicXML.

## Features

- Key transposition for guitar and bass tabs
- Random melody variation while preserving tab rhythm
- Guitar-to-bass translation
- Support for guitar, 4-string bass, and 5-string bass
- Timing grid controls for eighth, sixteenth, and triplet feels
- Clean guitar and bass browser playback with highlighted tab
- Local browser riff saving
- Text, MIDI, and MusicXML export

## Audio Preview

Older versions of this project used FluidSynth to convert MIDI files to WAV on the server. That required a native FluidSynth install, which made local setup brittle on Windows.

The current version avoids that native dependency. Flask still generates downloadable MIDI files with `midiutil`, but playback is handled in the browser from parsed note events. The primary preview path uses bundled clean guitar and bass samples; if sample loading fails, the app falls back to a lightweight Web Audio plucked-string model.

## Requirements

- Python 3.11 or newer
- pip

## Setup

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000/
```

## Usage

1. Use a sample preset or paste a text-based guitar/bass tab.
2. Choose the operation, key, scale, instrument, tuning, and timing grid.
3. Apply the transformation.
4. Preview the riff with clean guitar/bass audio and highlighted tab playback.
5. Copy or export the result as text, MIDI, or MusicXML.

## Example Tab

```text
e|----------------|----------------|----------------|------------------|
B|----------------|----------------|----------------|------------------|
G|-----3---5------|---3---6-5------|-----3---5----3-|------------------|
D|-5---3---5----5-|---3---6-5------|-5---3---5----3-|---5--------------|
A|-5------------5-|----------------|-5--------------|---5--------------|
E|----------------|----------------|----------------|------------------|
```

## Project Structure

```text
RiffEdit/
|-- Algcomposer.py       # Tab parsing, transformations, note events, and MIDI export
|-- app.py               # Flask application entry point
|-- requirements.txt     # Python dependencies
|-- static/              # CSS, images, and bundled soundfont samples
|-- templates/           # Flask templates
`-- Procfile             # Deployment config
```

## Soundfont Attribution

Bundled guitar and bass preview samples are generated from the FluidR3 GM soundfont through the `midi-js-soundfonts` project. FluidR3 GM is released under Creative Commons Attribution 3.0, and the `midi-js-soundfonts` project is MIT licensed.

Source: https://github.com/gleitz/midi-js-soundfonts

# RiffEdit

RiffEdit is a web application built with Python and Flask that allows users to input guitar or bass tabs and modify them by applying different musical transformations. The application can change the key of a tab, add randomness, translate guitar tabs into bass tabs, and even export the modified tab as a MIDI file for use in digital audio workstations (DAWs). It also supports converting MIDI files into WAV files for playback directly in the browser.

## Features

- **Key Transposition**: Change the key of the input guitar or bass tab while preserving the rhythm.
- **Random Melody Generation**: Introduce elements of randomness into the melody while maintaining the overall rhythm.
- **Guitar to Bass Tab Translation**: Translate a guitar tab into a bass tab (support for 4-string and 5-string bass).
- **Multiple Instruments and Tunings**: Handle standard tuning, drop D tuning, and half-step down tuning for guitar and bass.
- **MIDI Export**: Export the modified tab as a MIDI file, which can be used in DAWs like Ableton, GarageBand, and more.
- **WAV Playback**: Convert MIDI to WAV and play the audio directly in the web browser using FluidSynth.

## How It Works

1. **Input a Tab**: Enter a text-based guitar or bass tab into the web interface.
2. **Choose an Operation**: Select one of the available options:
   - Change key
   - Add randomness
   - Translate to bass
3. **Generate and Export**: The app will process the tab and return a modified version. You can export the result as a MIDI file or convert it to a WAV file and play it in the browser.

## Installation

### Prerequisites

- **Python 3.x**: Make sure Python 3 is installed on your system.
- **Flask**: For running the web server.
- **FluidSynth**: For converting MIDI files to WAV for playback.
- **MIDIUtil**: For creating MIDI files from guitar or bass tabs.

### Setting Up the Project

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/RiffEdit.git
    ```

2. Navigate into the project directory:
    ```bash
    cd RiffEdit
    ```

3. Create a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # For Linux/Mac
    .venv\Scripts\activate     # For Windows
    ```

4. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5. Download a **SoundFont** for MIDI-to-WAV conversion:
    - You can download **GeneralUser GS SoundFont** [here](https://schristiancollins.com/generaluser.php).
    - Place the SoundFont (`.sf2`) file in the `soundfonts/` folder.

### Running the Application

1. Run the Flask app:
    ```bash
    python app.py
    ```

2. Open your web browser and go to:
    ```
    http://127.0.0.1:5000/
    ```

3. Input your guitar/bass tabs, choose your desired options, and let the app process the tab. You can then export it as a MIDI file or play the generated WAV file.

## Usage

1. **Input Tab**: Paste a text-based guitar or bass tab into the input field.
2. **Choose Options**: Select the musical operation (e.g., change key, add randomness).
3. **Select Instrument**: Choose between guitar and bass (4-string or 5-string).
4. **Select Tuning**: Standard, Drop D, or Half-Step Down.
5. **Generate**: Click the button to generate the new tab. The output will be shown, and you can download it as a text file.
6. **MIDI and WAV**: You can also export the generated tab as a MIDI file or play it in your browser as a WAV.

## Example

Here is an example of a simple guitar tab that can be input into the app:

e|----------------|----------------|----------------|------------------| 
B|----------------|----------------|----------------|------------------| 
G|-----3---5------|---3---6-5------|-----3---5----3-|------------------| 
D|-5---3---5----5-|---3---6-5------|-5---3---5----3-|---5--------------| 
A|-5------------5-|----------------|-5--------------|---5--------------| 
E|----------------|----------------|----------------|------------------|


After processing, you can export this as a new tab in a different key, add randomness, or convert it to a bass tab.

## Project Structure

```plaintext
RiffEdit/
├── Algcomposer.py           # Main logic for tab processing and musical operations
├── Procfile                 # Deployment config for platforms like Heroku
├── README.md                # Documentation for the project
├── app.py                   # Flask application entry point
├── requirements.txt         # Dependencies for the project
├── static/
│   ├── CSS/
│   │   └── stylesheet.css   # Custom styles for the web app
│   └── soundfonts/          # Directory for storing SoundFont files
├── templates/
│   ├── index.html           # Main input page for the web app
│   ├── submitted.html       # Output page showing generated tabs
│   └── play_midi.html       # Page to play the generated MIDI as WAV
└── .gitignore               # Files and directories to be ignored by Git


Dependencies
The required Python libraries are listed in requirements.txt:
Flask==2.3.2
Jinja2==3.1.2
Werkzeug==2.3.4
setuptools>=58.0
FluidSynth
MIDIUtil
pyFluidSynth

Make sure to run pip install -r requirements.txt to install all dependencies before running the app.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Contributing
Contributions are welcome! If you have ideas for features or improvements, feel free to submit a pull request or open an issue.

Troubleshooting
Problem: FluidSynth not loading SoundFont correctly.
Solution: Make sure the .sf2 SoundFont file is in the correct directory (soundfonts/) and the path is correctly set in the code.
Problem: Unable to play WAV files in the browser.
Solution: Ensure the MIDI-to-WAV conversion is working properly and check the browser’s audio capabilities.



### Key Sections Added:
1. **Features**: Clearly outlines what the app does, which makes it easier for new users to understand the core functionality.
2. **Installation**: Detailed instructions for setting up the project, including dependencies and running the app.
3. **Usage**: A step-by-step guide to using the app, from inputting a tab to generating and downloading the result.
4. **Example**: A real-world example of input and output, which makes it easier for users to test the app.
5. **Project Structure**: An overview of the project structure to help developers navigate the code.
6. **Troubleshooting**: A small section on common issues and solutions.
7. **Contributing**: Encourages contributions to the project.

---

### Steps to Update:
1. Copy the content of this **`README.md`**.
2. Replace the content of your existing `README.md` file with this updated version.
3. Save the file.
4. Add, commit, and push the updated file:
   ```bash
   git add README.md
   git commit -m "Updated README.md with detailed instructions and feature set"
   git push origin master

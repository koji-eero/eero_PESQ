# eero PESQ - Auto Recording and PESQ Testing Tool

Voice-triggered automatic recording with audio alignment and PESQ quality assessment.

## Features

- 🎙️ Voice-triggered recording (starts automatically when sound is detected)
- ⏱️ Configurable recording duration (default: 25 seconds)
- 🔄 Automatic audio alignment using cross-correlation
- 📊 PESQ (Perceptual Evaluation of Speech Quality) score calculation
- 💾 Saves both original and aligned audio files
- 📝 Automatic file naming with PESQ score
- 🖥️ Cross-platform (Windows, macOS, Linux)

## Requirements

- Python 3.7 or higher
- Microphone/audio input device

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/eero_PESQ.git
cd eero_PESQ
```

### 2. Create virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install sounddevice soundfile scipy pesq numpy
```

Or install from requirements file:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python3 auto_record_and_pesq.py reference.wav
```

The script will:
1. Wait for voice trigger
2. Record for 25 seconds (default)
3. Save the recording as `Degraded_N_PESQ_X.XXX.wav`
4. Align the audio with the reference
5. Save aligned version as `Degraded_N_PESQ_X.XXX_aligned.wav`
6. Calculate and display PESQ score

### Advanced Options

```bash
# Custom recording duration (in seconds)
python3 auto_record_and_pesq.py reference.wav -d 30

# Adjust voice detection sensitivity (lower = more sensitive)
python3 auto_record_and_pesq.py reference.wav -t 0.01

# Specify sample rate (8000 or 16000 Hz)
python3 auto_record_and_pesq.py reference.wav -s 16000

# Combine options
python3 auto_record_and_pesq.py reference.wav -d 30 -t 0.01 -s 16000
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-d, --duration` | Recording duration in seconds | 25 |
| `-t, --threshold` | Voice detection threshold (0.0-1.0) | 0.03 |
| `-s, --sample-rate` | Sample rate: 8000 or 16000 Hz | 8000 |

## Output Files

The script generates two files per recording:

1. **Original recording**: `Degraded_N_PESQ_X.XXX.wav`
   - Raw recorded audio
   
2. **Aligned recording**: `Degraded_N_PESQ_X.XXX_aligned.wav`
   - Time-aligned with reference audio
   - Used for PESQ calculation

Where:
- `N` = Sequential number (1, 2, 3, ...)
- `X.XXX` = PESQ score (e.g., 4.210)

## PESQ Score Interpretation

| Score Range | Quality Rating |
|-------------|----------------|
| 4.0 - 4.5 | Excellent |
| 3.5 - 4.0 | Good |
| 3.0 - 3.5 | Fair |
| 2.5 - 3.0 | Poor |
| 1.0 - 2.5 | Bad |

## Requirements for Reference Audio

- Sample rate must be **8000 Hz** (narrowband) or **16000 Hz** (wideband)
- Must match the recording sample rate
- WAV format recommended

## Troubleshooting

### "Sample rate mismatch" error

Make sure your reference audio sample rate matches the recording sample rate:

```bash
# Check reference file sample rate
ffprobe reference.wav

# Convert to 8kHz if needed
ffmpeg -i input.wav -ar 8000 output_8k.wav

# Convert to 16kHz if needed
ffmpeg -i input.wav -ar 16000 output_16k.wav
```

### No audio input detected

- Check microphone permissions
- Verify microphone is working
- Try adjusting threshold: `-t 0.01` (more sensitive)

### "sounddevice" errors on Linux

Install PortAudio:

```bash
# Ubuntu/Debian
sudo apt-get install libportaudio2

# Fedora
sudo dnf install portaudio
```

## Example Workflow

```bash
# 1. Prepare reference audio (8kHz)
ffmpeg -i original.wav -ar 8000 reference_8k.wav

# 2. Run the tool
python3 auto_record_and_pesq.py reference_8k.wav

# 3. Wait for voice trigger message
# 4. Play audio or speak into microphone
# 5. Recording automatically stops after 25 seconds
# 6. View PESQ results in terminal
```

## License

MIT License

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

# Video to PDF Converter

## Prerequisites
- macOS (Homebrew will be automatically installed if not present)

## Setup Options

### Option 1: Traditional Setup (using setup.sh)
1. Make the setup script executable:
   ```bash
   chmod +x setup.sh
   ```
2. Run the setup script:
   ```bash
   ./setup.sh
   ```

### Option 2: Poetry Setup
1. Install Poetry if not installed:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Install system dependencies:
   ```bash
   poetry run setup-deps
   ```
4. Run the application:
   ```bash
   poetry run python app.py
   ```

## Usage

### GUI Version
Run the graphical interface:
```bash
python gui.py
```

The GUI provides:
- Video file selection button
- Two extraction methods:
  1. Fixed intervals (default: 0.5 seconds)
  2. Scene detection (threshold: 0.3)
- Option to enable/disable OCR text extraction
- Progress indicator
- Direct access to output folder

### Command Line Version
Run from command line:
```bash
python app.py
```

You can import and use the processing function in your code:
```python
from app import process_video

# Method 1: Fixed intervals
process_video("path/to/video.mp4", method="1", param=0.5, extract_text=True)

# Method 2: Scene detection
process_video("path/to/video.mp4", method="2", param=0.3, extract_text=True)
```

Parameters:
- `method`: "1" for fixed intervals, "2" for scene detection
- `param`: 
  - For method "1": interval in seconds (default: 0.5)
  - For method "2": scene change threshold (default: 0.3)
- `extract_text`: Enable/disable OCR (default: True)

### Output Location
Files are saved in:
```
~/Documents/Downloads Documents/Video_to_PDF_output/
```

Output files:
- `output.pdf`: Contains extracted frames
- `output.md`: Contains OCR-extracted text (if enabled)

### Tips
- For clearer text extraction, use method "2" (scene detection)
- Adjust the threshold/interval based on video content:
  - Presentations: longer intervals (1-2 seconds)
  - Dynamic content: shorter intervals (0.3-0.5 seconds)
- The GUI provides real-time progress feedback
- Check the output folder directly through the GUI's "Open Output Folder" button
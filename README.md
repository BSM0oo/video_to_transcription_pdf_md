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
Run with:
```bash
python app.py
```

The program will create:
- A markdown file with extracted text
- A PDF containing all slides
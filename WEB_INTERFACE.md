# Web Interface Guide

The Pokemon Scouter now includes a web-based interface for generating scout reports.

## Running the Web App

1. Install Flask (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

2. Run the web app:
   ```bash
   python web_app.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Enter Usernames**: Comma-separated list of target usernames (e.g., `player1, player2`)
2. **Select Tier**: The tier to scout for (e.g., `gen8ou`, `gen7ou`)
3. **Add Tours**: Click "Add Tour" to add tournament data
   - Enter the **Tour Name** (e.g., Masters, RCoP, OUPL)
   - Paste **Replay URLs** one per line (can be full URLs or `/simulate/` URLs)
4. **Generate**: Click "Generate Importable" to process the replays
5. **Download**: Download the results as a text file or copy from the output

## Architecture

### Model (`web/models.py`)
- `ScoutRequest`: Data class for form input
- `Tour`: Data class for tournament data
- Handles validation and parsing of user input

### Controller (`web/controllers.py`)
- `ScoutController`: Orchestrates scout generation
- Calls existing parser and sorter modules
- Returns formatted output

### View (`web/templates/index.html`)
- HTML form with dynamic tour management
- Results display and download functionality

### Static Files (`web/static/`)
- `script.js`: Form handling, dynamic tour addition, API calls
- `style.css`: Responsive styling with gradient background

## Technical Details

- **Framework**: Flask
- **Frontend**: Vanilla HTML/CSS/JavaScript (no dependencies)
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: Validation on both frontend and backend

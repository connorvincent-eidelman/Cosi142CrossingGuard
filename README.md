# Overtake Events Dashboard

A Flask web application that displays overtake events from a CSV file with automatic 30-second refresh intervals.

## Features

- 📊 Real-time data display from `overtake_events.csv`
- 🔄 Automatic refresh every 30 seconds
- 📱 Responsive design (works on desktop and mobile)
- ✨ Clean, modern UI with gradient styling
- ⏱️ Last update timestamp and event count

## Project Structure

```
car_videos/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── overtake_events.csv    # Data file (read by app)
├── templates/
│   └── index.html         # Main HTML template
└── static/
    ├── style.css          # Styling
    └── script.js          # Client-side logic
```

## Installation

1. Ensure you're in the project directory:

```bash
cd /Users/connorv-e/car_videos
```

2. Activate your virtual environment (if you have one):

```bash
source .venv/bin/activate
```

3. Install Flask (if not already in requirements):

```bash
pip install flask
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:

```bash
python app.py
```

2. Open your browser and navigate to:

```
http://127.0.0.1:5000
```

3. The page will automatically refresh every 30 seconds to show updated data from the CSV file.

4. You can also manually refresh by pressing `R` on your keyboard.

## Stopping the Server

Press `Ctrl+C` in the terminal where the Flask server is running.

## Customization

- **Change refresh interval**: Edit `static/script.js` and change the `30000` value (milliseconds) in the `setInterval` call
- **Change port**: Edit `app.py` and modify the `port=5000` parameter
- **Change CSV file**: Edit the `CSV_FILE` path in `app.py`

## Notes

- The CSV file must exist and be readable
- Column headers from the CSV will automatically become table headers
- The application assumes the CSV file uses standard comma-separated format with headers in the first row

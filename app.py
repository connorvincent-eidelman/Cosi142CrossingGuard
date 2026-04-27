from flask import Flask, render_template, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)

# Path to the CSV file
CSV_FILE = os.path.join(os.path.dirname(__file__), 'overtake_events.csv')

def read_csv():
    """Read and return CSV data as a list of dictionaries"""
    if not os.path.exists(CSV_FILE):
        return []
    
    data = []
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return data

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """API endpoint to get CSV data as JSON"""
    data = read_csv()
    return jsonify({
        'data': data,
        'timestamp': datetime.now().isoformat(),
        'row_count': len(data)
    })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

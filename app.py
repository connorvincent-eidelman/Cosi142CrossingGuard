from flask import Flask, render_template, jsonify
import csv
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# Path to the CSV files
CSV_FILE = os.path.join(os.path.dirname(__file__), 'overtake_events.csv')
DATA_CSV_FILE = os.path.join(os.path.dirname(__file__), 'overtake_data.csv')

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

def analyze_traffic():
    """Analyze overtake_data.csv to find peak traffic times by timestamp"""
    if not os.path.exists(DATA_CSV_FILE):
        return {'error': 'Data file not found'}
    
    traffic_by_time = defaultdict(lambda: {'count': 0, 'unique_cars': set(), 'frames': 0})
    
    try:
        with open(DATA_CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    timestamp = row['Timestamp']
                    car_id = row['Car_ID']
                    
                    # Parse timestamp and extract hour:minute
                    dt = datetime.fromisoformat(timestamp)
                    time_key = dt.strftime('%H:%M')
                    
                    traffic_by_time[time_key]['count'] += 1
                    traffic_by_time[time_key]['unique_cars'].add(car_id)
                    traffic_by_time[time_key]['frames'] += 1
                except (ValueError, KeyError):
                    continue
    except Exception as e:
        return {'error': f'Error analyzing data: {e}'}
    
    # Convert to list and sort by time
    traffic_timeline = []
    for time_key in sorted(traffic_by_time.keys()):
        data = traffic_by_time[time_key]
        traffic_timeline.append({
            'time': time_key,
            'time_display': f'{time_key}',
            'detections': data['count'],
            'unique_cars': len(data['unique_cars']),
            'frames': data['frames']
        })
    
    # Find peak traffic time
    peak_time = max(traffic_timeline, key=lambda x: x['detections']) if traffic_timeline else None
    average_detections = sum(x['detections'] for x in traffic_timeline) / len(traffic_timeline) if traffic_timeline else 0
    
    return {
        'timeline': traffic_timeline,
        'peak_time': peak_time,
        'average_detections': average_detections,
        'total_unique_cars': len(set(row['Car_ID'] for row in csv.DictReader(open(DATA_CSV_FILE, 'r')) if 'Car_ID' in row))
    }

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

@app.route('/api/traffic-analysis')
def get_traffic_analysis():
    """API endpoint to get traffic analysis"""
    return jsonify(analyze_traffic())

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

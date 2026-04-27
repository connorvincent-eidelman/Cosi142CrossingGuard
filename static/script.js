// Tab switching functionality
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        
        // Remove active class from all tabs and buttons
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        
        // Add active class to clicked button and corresponding tab
        btn.classList.add('active');
        document.getElementById(`${tab}-tab`).classList.add('active');
        
        // Load traffic analysis when switching to traffic tab
        if (tab === 'traffic') {
            fetchTrafficAnalysis();
        }
    });
});

// Fetch data and update the table
async function fetchAndUpdateData() {
    try {
        const response = await fetch('/api/data');
        const result = await response.json();
        
        updateTable(result.data);
        updateTimestamp(result.timestamp);
        updateRowCount(result.row_count);
    } catch (error) {
        console.error('Error fetching data:', error);
        document.getElementById('table-body').innerHTML = 
            '<tr><td colspan="100%" class="loading">Error loading data. Retrying...</td></tr>';
    }
}

// Update the table with data
function updateTable(data) {
    const tableBody = document.getElementById('table-body');
    const headerRow = document.getElementById('header-row');
    
    // Clear existing content
    tableBody.innerHTML = '';
    
    if (data.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="100%" class="loading">No data available</td></tr>';
        return;
    }
    
    // Create headers if not already present
    if (headerRow.children.length === 0) {
        const headers = Object.keys(data[0]);
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });
    }
    
    // Populate table rows
    data.forEach(row => {
        const tr = document.createElement('tr');
        Object.values(row).forEach(value => {
            const td = document.createElement('td');
            td.textContent = value;
            tr.appendChild(td);
        });
        tableBody.appendChild(tr);
    });
}

// Update timestamp
function updateTimestamp(timestamp) {
    const date = new Date(timestamp);
    const formattedTime = date.toLocaleTimeString();
    document.getElementById('timestamp').textContent = formattedTime;
}

// Update row count
function updateRowCount(count) {
    document.getElementById('row-count').textContent = count;
}

// Fetch and display traffic analysis
async function fetchTrafficAnalysis() {
    try {
        const response = await fetch('/api/traffic-analysis');
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('traffic-tbody').innerHTML = 
                `<tr><td colspan="5" class="loading">Error: ${data.error}</td></tr>`;
            return;
        }
        
        updateTrafficSummary(data);
        updateTrafficChart(data.timeline);
        updateTrafficTable(data.timeline);
    } catch (error) {
        console.error('Error fetching traffic analysis:', error);
    }
}

// Update traffic summary cards
function updateTrafficSummary(data) {
    if (data.peak_time) {
        document.getElementById('peak-time').textContent = data.peak_time.time_display;
        document.getElementById('peak-count').textContent = `${data.peak_time.detections} detections`;
    }
    
    document.getElementById('avg-traffic').textContent = data.average_detections.toFixed(1);
    document.getElementById('unique-cars').textContent = data.total_unique_cars;
}

// Update traffic chart
function updateTrafficChart(timeline) {
    const chartContainer = document.getElementById('traffic-chart');
    chartContainer.innerHTML = '';
    
    if (timeline.length === 0) {
        chartContainer.innerHTML = '<p class="loading">No data available</p>';
        return;
    }
    
    // Find max detections for scaling
    const maxDetections = Math.max(...timeline.map(t => t.detections));
    
    timeline.forEach(timePoint => {
        const bar = document.createElement('div');
        bar.className = 'traffic-bar';
        
        // Scale bar height
        const height = (timePoint.detections / maxDetections) * 100;
        bar.style.height = `${height}%`;
        
        // Add label
        const label = document.createElement('div');
        label.className = 'traffic-bar-label';
        label.textContent = timePoint.time_display;
        bar.appendChild(label);
        
        // Add tooltip on hover
        bar.title = `${timePoint.time_display}: ${timePoint.detections} detections, ${timePoint.unique_cars} unique cars`;
        
        chartContainer.appendChild(bar);
    });
}

// Update traffic table
function updateTrafficTable(timeline) {
    const tbody = document.getElementById('traffic-tbody');
    tbody.innerHTML = '';
    
    if (timeline.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">No data available</td></tr>';
        return;
    }
    
    // Find max detections for density bar
    const maxDetections = Math.max(...timeline.map(t => t.detections));
    
    timeline.forEach(timePoint => {
        const tr = document.createElement('tr');
        
        const densityPercent = (timePoint.detections / maxDetections) * 100;
        
        tr.innerHTML = `
            <td>${timePoint.time_display}</td>
            <td>${timePoint.detections}</td>
            <td>${timePoint.unique_cars}</td>
            <td>${timePoint.frames}</td>
            <td>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="density-bar" style="width: ${densityPercent}px;"></div>
                    <span>${densityPercent.toFixed(0)}%</span>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Fetch data immediately
    fetchAndUpdateData();
    
    // Set up periodic refresh (30 seconds = 30000 ms)
    setInterval(fetchAndUpdateData, 30000);
});

// Optional: Add a manual refresh button functionality
document.addEventListener('keydown', (e) => {
    // Press 'R' to manually refresh
    if (e.key === 'r' || e.key === 'R') {
        console.log('Manual refresh triggered');
        fetchAndUpdateData();
        // Also refresh traffic data if on that tab
        if (document.getElementById('traffic-tab').classList.contains('active')) {
            fetchTrafficAnalysis();
        }
    }
});

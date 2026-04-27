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
    }
});

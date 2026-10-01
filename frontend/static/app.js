// Configuration
const API_BASE = window.location.origin;
let map;
let drawnItems = {};

// Initialize map on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeMap();
    checkSystemStatus();
    updateWeightDisplay();
});

// Initialize Leaflet map
function initializeMap() {
    map = L.map('map').setView([20, 0], 4);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Initialize drawnItems
    drawnItems = {
        startMarker: null,
        endMarker: null,
        routePolyline: null,
        riskLayer: null
    };
}

// Check system status
async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        const statusDiv = document.getElementById('status');
        statusDiv.innerHTML = `
            <p><strong>Hazard Layers:</strong> ${data.hazard_layers_loaded}</p>
            <p><strong>Risk Index:</strong> ${data.risk_index_calculated ? 'Calculated' : 'Pending'}</p>
            <p><strong>Router Status:</strong> ${data.router_ready ? 'Ready' : 'Not Ready'}</p>
        `;
    } catch (error) {
        console.error('Status check failed:', error);
        document.getElementById('status').innerHTML = '<p style="color: red;">Connection failed</p>';
    }
}

// Update weight display values
function updateWeightDisplay() {
    const weights = ['flood', 'landslide', 'slope', 'settlement'];
    let total = 0;

    weights.forEach(w => {
        const input = document.getElementById(w);
        const value = parseFloat(input.value);
        total += value;
        document.getElementById(`${w}-value`).textContent = value.toFixed(2);
    });

    const warning = document.getElementById('sum-warning');
    if (Math.abs(total - 1.0) > 0.01) {
        warning.textContent = `⚠ Weights sum to ${total.toFixed(2)} (should be 1.0)`;
        warning.style.color = '#ff9800';
    } else {
        warning.textContent = '✓ Weights sum correctly';
        warning.style.color = '#4caf50';
    }
}

// Update weight display on range input change
document.querySelectorAll('input[type="range"]').forEach(input => {
    input.addEventListener('input', updateWeightDisplay);
});

// Calculate risk index
async function calculateRisk() {
    try {
        const weights = {
            flood: parseFloat(document.getElementById('flood').value),
            landslide: parseFloat(document.getElementById('landslide').value),
            slope: parseFloat(document.getElementById('slope').value),
            proximity_settlements: parseFloat(document.getElementById('settlement').value)
        };

        // Validate weights sum to ~1.0
        const total = Object.values(weights).reduce((a, b) => a + b, 0);
        if (Math.abs(total - 1.0) > 0.01) {
            alert(`Weights must sum to 1.0, current sum: ${total.toFixed(2)}`);
            return;
        }

        const response = await fetch(`${API_BASE}/risk/calculate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(weights)
        });

        if (!response.ok) throw new Error(await response.text());

        const data = await response.json();
        alert(`✓ Risk index calculated!\nMin: ${data.risk_min.toFixed(2)}, Max: ${data.risk_max.toFixed(2)}, Mean: ${data.risk_mean.toFixed(2)}`);
        checkSystemStatus();
        
        // Visualize risk index (simplified - showing gradient)
        visualizeRiskLayer();
    } catch (error) {
        alert(`Error calculating risk: ${error.message}`);
    }
}

// Visualize risk index layer
function visualizeRiskLayer() {
    // Create a gradient visualization on the map
    if (drawnItems.riskLayer) {
        map.removeLayer(drawnItems.riskLayer);
    }

    // Add a simple gradient rectangle as visualization
    const bounds = map.getBounds();
    const gradient = L.rectangle(bounds, {
        color: 'transparent',
        fillColor: 'red',
        fillOpacity: 0.3,
        weight: 0
    }).addTo(map);

    drawnItems.riskLayer = gradient;
}

// Identify high-risk locations
async function identifyHighRisk() {
    try {
        const threshold = parseFloat(prompt('Enter risk threshold (0-1):', '0.6')) || 0.6;

        const response = await fetch(`${API_BASE}/risk/high-risk-locations?threshold=${threshold}`, {
            method: 'POST'
        });

        if (!response.ok) throw new Error(await response.text());

        const data = await response.json();
        const statsDiv = document.getElementById('risk-stats');
        statsDiv.innerHTML = `
            <p><strong>Threshold:</strong> ${data.threshold}</p>
            <p><strong>High-Risk Pixels:</strong> ${data.count.toLocaleString()}</p>
            <p>${data.message}</p>
        `;
    } catch (error) {
        alert(`Error identifying high-risk areas: ${error.message}`);
    }
}

// Find least-risk route
async function findRoute() {
    try {
        const startStr = document.getElementById('start-point').value;
        const endStr = document.getElementById('end-point').value;

        if (!startStr || !endStr) {
            alert('Please enter both start and end points');
            return;
        }

        const [sr, sc] = startStr.split(',').map(x => parseInt(x.trim()));
        const [er, ec] = endStr.split(',').map(x => parseInt(x.trim()));

        const response = await fetch(`${API_BASE}/routing/find-path`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start: [sr, sc],
                end: [er, ec],
                alternative_count: 1
            })
        });

        if (!response.ok) throw new Error(await response.text());

        const data = await response.json();
        
        // Clear previous markers and routes
        if (drawnItems.startMarker) map.removeLayer(drawnItems.startMarker);
        if (drawnItems.endMarker) map.removeLayer(drawnItems.endMarker);
        if (drawnItems.routePolyline) map.removeLayer(drawnItems.routePolyline);

        // Add start marker (red)
        drawnItems.startMarker = L.circleMarker(L.latLng(sr, sc), {
            radius: 8,
            fillColor: '#ff0000',
            color: '#000',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map).bindPopup('Start Point');

        // Add end marker (blue)
        drawnItems.endMarker = L.circleMarker(L.latLng(er, ec), {
            radius: 8,
            fillColor: '#0000ff',
            color: '#000',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map).bindPopup('End Point');

        // Draw route (green polyline)
        const pathCoords = data.path.map(p => L.latLng(p[0], p[1]));
        drawnItems.routePolyline = L.polyline(pathCoords, {
            color: '#00aa00',
            weight: 3,
            opacity: 0.8
        }).addTo(map).bindPopup(`Route Cost: ${data.cost.toFixed(2)}<br>Risk: ${data.risk_level}`);

        // Update info
        const routeInfo = document.getElementById('route-info');
        routeInfo.innerHTML = `
            <p><strong>Route Found!</strong></p>
            <p>Cost: ${data.cost.toFixed(2)}</p>
            <p>Risk Level: ${data.risk_level}</p>
            <p>Path Points: ${data.path.length}</p>
        `;

        // Fit map to route
        map.fitBounds(L.featureGroup([
            drawnItems.startMarker,
            drawnItems.endMarker,
            drawnItems.routePolyline
        ]).getBounds());
    } catch (error) {
        alert(`Error finding route: ${error.message}`);
    }
}

// Find alternative routes
async function findAlternatives() {
    try {
        const startStr = document.getElementById('start-point').value;
        const endStr = document.getElementById('end-point').value;

        if (!startStr || !endStr) {
            alert('Please enter both start and end points');
            return;
        }

        const [sr, sc] = startStr.split(',').map(x => parseInt(x.trim()));
        const [er, ec] = endStr.split(',').map(x => parseInt(x.trim()));

        const response = await fetch(`${API_BASE}/routing/alternatives`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start: [sr, sc],
                end: [er, ec],
                alternative_count: 3
            })
        });

        if (!response.ok) throw new Error(await response.text());

        const data = await response.json();

        // Display route information
        let routeInfo = `<p><strong>${data.routes_found} Alternative Routes Found</strong></p>`;
        data.routes.forEach((route, idx) => {
            routeInfo += `<p>Route ${idx + 1}: Cost ${route.cost.toFixed(2)}, Points: ${route.length}</p>`;
        });

        document.getElementById('route-info').innerHTML = routeInfo;
        alert(`Found ${data.routes_found} alternative routes`);
    } catch (error) {
        alert(`Error finding alternatives: ${error.message}`);
    }
}

// Periodic status updates
setInterval(checkSystemStatus, 10000);

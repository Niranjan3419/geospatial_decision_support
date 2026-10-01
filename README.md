# Geospatial Decision Support System

A comprehensive web-based platform for **multi-hazard risk assessment** and **emergency route optimization** during disasters. This hackathon project integrates flood, landslide, and slope hazards into a unified decision-support framework using Multi-Criteria Decision Making (MCDM) and least-risk pathfinding algorithms.

## Features

### 🗺️ Hazard Layer Processing
- Load and normalize individual hazard layers (flood, landslide, slope)
- Support for raster (GeoTIFF) and vector (Shapefile/GeoJSON) data formats
- Automatic data normalization and validation

### 📊 Multi-Criteria Decision Making (MCDM)
- Weighted risk index calculation combining multiple hazards
- Configurable weights for different criteria
- Dynamic weight adjustment for scenario analysis
- Identification of high-risk zones

### 🛣️ Emergency Routing
- Least-risk path finding algorithm (not just shortest distance)
- Network-aware routing using road networks
- Alternative route suggestions
- Risk level classification (Low/Medium/High)

### 🌐 Interactive Web Visualization
- Real-time interactive map using Leaflet.js
- Risk layer visualization with color gradients
- Route overlay with start/end point markers
- Responsive UI for desktop and mobile

## Project Structure

```
geospatial_decision_support/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI application server
│   │   ├── __init__.py
│   │   └── services/          # Core business logic
│   │       ├── hazard_processor.py    # Hazard layer processing
│   │       ├── mcdm.py                # MCDM risk calculation
│   │       ├── routing.py             # Emergency routing engine
│   │       └── __init__.py
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment configuration
├── frontend/                   # Web UI (HTML/CSS/JavaScript)
│   ├── templates/
│   │   └── index.html         # Main web interface
│   └── static/
│       ├── style.css          # UI styling
│       └── app.js             # Frontend logic & API client
├── data/                       # Data directory
│   ├── raw/                   # Raw input data (GIS files)
│   └── processed/             # Processed outputs
├── docs/                       # Documentation
├── README.md                   # This file
└── .gitignore
```

## Technical Stack

### Backend
- **FastAPI**: Modern Python web framework with automatic API documentation
- **GeoPandas**: Vector geospatial data manipulation
- **Rasterio**: Raster data processing
- **NetworkX**: Graph-based routing algorithms
- **NumPy/SciPy**: Numerical computations

### Frontend
- **Leaflet.js**: Interactive mapping library
- **OpenStreetMap**: Base map tiles
- **Vanilla JavaScript**: Frontend logic

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js (optional, for frontend development)
- Git

### Backend Setup

1. **Clone and navigate to project:**
   ```bash
   cd geospatial_decision_support
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Start backend server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend API available at: `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Start simple HTTP server:**
   ```bash
   # Python 3
   python -m http.server 8001
   
   # Or use Node http-server
   npx http-server -p 8001
   ```

3. **Open in browser:**
   Navigate to `http://localhost:8001/templates/index.html`

## API Endpoints

### System Status
- `GET /` - Root endpoint
- `GET /status` - System status and initialization state
- `GET /health` - Health check

### Hazard Management
- `POST /hazards/summary` - Get loaded hazard layers summary

### Risk Assessment
- `POST /risk/calculate` - Calculate multi-hazard risk index
  - Body: `{flood, landslide, slope, proximity_settlements}` (weights)
- `POST /risk/high-risk-locations` - Identify high-risk zones
  - Query: `threshold` (0-1)

### Emergency Routing
- `POST /routing/find-path` - Find least-risk route
  - Body: `{start: [row, col], end: [row, col], alternative_count: int}`
- `POST /routing/alternatives` - Get alternative routes
  - Body: `{start: [row, col], end: [row, col], alternative_count: int}`

### Example API Usage

```bash
# Calculate risk index with custom weights
curl -X POST http://localhost:8000/risk/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "flood": 0.35,
    "landslide": 0.35,
    "slope": 0.20,
    "proximity_settlements": 0.10
  }'

# Find least-risk route
curl -X POST http://localhost:8000/routing/find-path \
  -H "Content-Type: application/json" \
  -d '{
    "start": [100, 100],
    "end": [200, 200],
    "alternative_count": 1
  }'
```

## Data Format

### Input Data Requirements

**Raster Hazard Data:**
- Format: GeoTIFF (.tif, .tiff)
- Location: `data/raw/`
- File naming: `[hazard_type]_layer.tif`
  - Example: `flood_layer.tif`, `landslide_layer.tif`, `slope_layer.tif`
- Projection: WGS84 (EPSG:4326) or UTM
- NoData value: -9999

**Vector Data:**
- Format: Shapefile (.shp) or GeoJSON (.geojson)
- Location: `data/raw/`
- Include: Roads network, settlements, shelters, hospitals

### Output Data
- Processed layers: `data/processed/`
- Risk index: `risk_index.tif`
- High-risk zones: `high_risk_zones.shp`
- Optimal routes: `routes.geojson`

## Workflow

### Step 1: Data Preparation
1. Gather hazard layers (flood, landslide, slope maps)
2. Prepare road network data
3. Identify settlements, hospitals, shelters
4. Place files in `data/raw/` directory

### Step 2: Hazard Normalization
- Each hazard layer is normalized to 0-1 scale
- Handles different units and scales automatically

### Step 3: MCDM Risk Calculation
1. Adjust weights in web UI (or via API)
2. Click "Calculate Risk Index"
3. System combines hazards into unified risk map

### Step 4: Risk Analysis
1. Visualize multi-hazard risk layer on interactive map
2. Identify high-risk zones using configurable threshold
3. Export risk statistics

### Step 5: Emergency Routing
1. Select start and end points on map
2. System calculates least-risk path (not shortest)
3. View alternative routes
4. Export optimal evacuation routes

## MCDM Methodology

The system uses weighted linear combination for risk assessment:

```
Risk Index = w_flood × Flood_norm + w_landslide × Landslide_norm 
           + w_slope × Slope_norm + w_settlement × Settlement_proximity
```

Where:
- Each indicator is normalized to [0, 1]
- Weights sum to 1.0
- Higher values = higher risk
- Thresholds identify high-risk zones

## Routing Algorithm

The emergency routing engine uses Dijkstra's algorithm with custom cost function:

```
Cost = Distance × (1 + Risk_Level)
```

This ensures routes avoid high-risk areas while minimizing travel distance.

## Contributing

To contribute to this project:
1. Create a feature branch: `git checkout -b feature/new-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push branch: `git push origin feature/new-feature`
4. Submit pull request

## Team

- **Architecture & Backend**: Core geospatial processing and API
- **Frontend**: Interactive web mapping interface
- **MCDM & Routing**: Decision support algorithms

## Hackathon Challenge

This project addresses the challenge of developing an integrated geospatial decision-support system for emergency management:

✅ **Challenge Requirements Met:**
- ✓ Multi-hazard integration (flood, landslide, slope)
- ✓ Indicator normalization
- ✓ MCDM-based risk index
- ✓ High-risk location identification
- ✓ Least-risk emergency routing (not shortest-distance)
- ✓ Web-based visualization
- ✓ Interactive emergency route mapping

## Future Enhancements

- [ ] Real-time hazard monitoring integration
- [ ] Machine learning-based risk prediction
- [ ] Mobile app for field operations
- [ ] Multi-modal routing (walk, vehicle, emergency transport)
- [ ] Shelter capacity and allocation optimization
- [ ] Real-time traffic/congestion integration
- [ ] Advanced MCDM methods (AHP, TOPSIS, Fuzzy logic)
- [ ] 3D visualization and drone integration
- [ ] Disaster simulation and scenario planning

## License

This project is provided as-is for hackathon competition purposes.

## Contact

For questions or issues, please refer to the project documentation or create an issue in the repository.

---

**Last Updated:** October 2026
**Status:** Hackathon Project (Alpha)
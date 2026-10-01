# Technical Architecture

## System Overview

The Geospatial Decision Support System is built on a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│           Web UI (Frontend)                              │
│      HTML/CSS/JavaScript + Leaflet.js                   │
│     (Interactive map visualization)                      │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │   HTTP REST API     │
        │    (FastAPI)        │
        └──────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐  ┌─────▼─────┐  ┌─────▼────┐
│Hazard  │  │ MCDM Risk │  │ Emergency│
│Proc.   │  │ Calc.     │  │ Routing  │
└────────┘  └───────────┘  └──────────┘
    │              │              │
    └──────────────┼──────────────┘
                   │
    ┌──────────────▼──────────────┐
    │   Data Layer                 │
    │  (GIS files, rasters, etc)  │
    └──────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

**Location**: `frontend/`

#### Components:
- **index.html**: Main UI layout with sidebar and map
- **style.css**: Responsive design for desktop/mobile
- **app.js**: API client and Leaflet.js integration

#### Responsibilities:
- User interaction and control
- Real-time map visualization
- MCDM weight configuration
- Route visualization
- RESTful API calls to backend

#### Technologies:
- Leaflet.js (mapping library)
- OpenStreetMap (base tiles)
- Vanilla JavaScript (no frameworks)

---

### 2. API Layer (FastAPI)

**Location**: `backend/app/main.py`

#### Endpoints:

| Category | Endpoint | Method | Purpose |
|----------|----------|--------|---------|
| **System** | `/` | GET | Root endpoint |
| | `/status` | GET | System status |
| | `/health` | GET | Health check |
| **Hazards** | `/hazards/summary` | POST | Get loaded layers |
| **Risk** | `/risk/calculate` | POST | Compute risk index |
| | `/risk/high-risk-locations` | POST | Find high-risk zones |
| **Routes** | `/routing/find-path` | POST | Optimal route |
| | `/routing/alternatives` | POST | Alternative routes |

#### Features:
- Automatic OpenAPI/Swagger documentation at `/docs`
- CORS middleware for frontend integration
- Pydantic models for request validation
- Async request handling

#### Middleware:
- CORS: Allow cross-origin requests
- JSON content type handling
- Error handling and HTTP status codes

---

### 3. Business Logic Layer

**Location**: `backend/app/services/`

#### A. Hazard Processor (`hazard_processor.py`)

Handles geospatial data input:

```python
class HazardProcessor:
    - load_raster_hazard()      # Read GeoTIFF files
    - load_vector_hazard()      # Read Shapefile/GeoJSON
    - normalize_hazard()        # Scale to [0,1]
    - get_hazard_summary()      # List loaded layers
```

**Methods**:
- Min-Max normalization: scales data to [0,1]
- Z-score normalization: statistical normalization
- NoData handling: preserves invalid pixels
- Multiple data format support

#### B. MCDM Risk Calculator (`mcdm.py`)

Multi-Criteria Decision Making engine:

```python
class McdmRiskCalculator:
    - calculate_risk_index()           # Weighted combination
    - identify_high_risk_locations()   # Threshold analysis
    - update_weights()                 # Dynamic reweighting
```

**Algorithm**:
```
Risk = Σ(weight_i × normalized_indicator_i)
```

**Weights**:
- Flood: 0.35 (default)
- Landslide: 0.35 (default)
- Slope: 0.20 (default)
- Settlement Proximity: 0.10 (default)

#### C. Least-Risk Router (`routing.py`)

Pathfinding with risk integration:

```python
class LeastRiskRouter:
    - create_road_graph()          # Build network graph
    - find_least_risk_path()       # Dijkstra's algorithm
    - get_alternative_routes()     # k-shortest paths
```

**Cost Function**:
```
Edge Cost = Distance × (1 + avg_risk)
```

**Algorithm**:
- Dijkstra's algorithm for shortest path
- 8-connectivity for grid-based movement
- NetworkX for graph operations

---

### 4. Data Layer

**Location**: `data/`

#### Structure:
```
data/
├── raw/               # Input GIS data
│   ├── flood_layer.tif
│   ├── landslide_layer.tif
│   ├── slope_layer.tif
│   └── road_network.shp
└── processed/         # Output results
    ├── risk_index.tif
    ├── high_risk_zones.shp
    └── routes.geojson
```

#### Supported Formats:
- **Raster**: GeoTIFF (.tif, .tiff)
- **Vector**: Shapefile (.shp), GeoJSON (.geojson)
- **Projection**: WGS84 (EPSG:4326) or UTM

---

## Data Flow

### Workflow 1: Risk Assessment

```
Load GIS Data
    ↓
Normalize Hazard Layers (0-1)
    ↓
Apply MCDM Weights
    ↓
Calculate Composite Risk Index
    ↓
Identify High-Risk Zones
    ↓
Visualize on Map
```

### Workflow 2: Emergency Routing

```
Select Start/End Points
    ↓
Create Network Graph (Road)
    ↓
Weight Edges with Risk
    ↓
Apply Dijkstra's Algorithm
    ↓
Return Least-Risk Path
    ↓
Display on Map + Alternatives
```

---

## Key Technologies

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.8+ | Runtime |
| FastAPI | 0.104+ | Web framework |
| GeoPandas | 0.14+ | Vector geospatial |
| Rasterio | 1.3+ | Raster processing |
| NetworkX | 3.2+ | Graph algorithms |
| NumPy | 1.24+ | Numerical computing |
| Uvicorn | 0.24+ | ASGI server |

### Frontend
| Technology | Purpose |
|-----------|---------|
| Leaflet.js | Interactive mapping |
| OpenStreetMap | Base layer tiles |
| Vanilla JavaScript | Frontend logic |
| CSS3 | Responsive design |
| HTML5 | Semantic markup |

---

## Performance Considerations

### Optimization Strategies

1. **Data Processing**:
   - NumPy vectorization for raster operations
   - Efficient array slicing for normalization
   - In-memory caching of loaded hazards

2. **Routing**:
   - Graph pre-computation
   - Dijkstra with early termination
   - Edge weight caching

3. **API Response**:
   - Async request handling
   - Minimal JSON serialization
   - Efficient coordinate encoding

4. **Frontend**:
   - Canvas-based rendering (Leaflet)
   - Lazy loading of map tiles
   - Client-side calculation caching

---

## Security & Validation

### Input Validation
- Pydantic models for API requests
- Coordinate bounds checking
- Weight sum validation (must equal 1.0)
- File type verification

### CORS Policy
- Allow frontend localhost
- Configure for production deployment
- Prevent unauthorized API access

### Error Handling
- Try-catch blocks for file I/O
- Graceful HTTP error responses
- Detailed error messages for debugging

---

## Scalability

### Current Limitations
- Single-server architecture
- Memory-based data storage
- Synchronous processing

### Future Scaling Options
1. **Distributed Processing**: Dask for parallel raster operations
2. **Caching**: Redis for API response caching
3. **Database**: PostgreSQL + PostGIS for persistent data
4. **Cloud Deployment**: AWS Lambda, Google Cloud Functions
5. **Real-time Updates**: WebSockets for live hazard monitoring

---

## Testing & Quality

### Testing Strategy
- Unit tests for individual components
- Integration tests for API endpoints
- Manual testing of UI workflows

### Logging
- Backend logging via Python logging module
- Frontend console logging
- API request/response logging

---

## Deployment

### Development
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000

cd frontend
python -m http.server 8001
```

### Production
- Use Uvicorn with Gunicorn for backend
- Serve frontend via Nginx or CloudFront
- Configure environment variables
- Enable HTTPS/SSL
- Set up database persistence

---

## Future Extensions

### Phase 2
- Real-time hazard data integration
- ML-based risk prediction
- Advanced MCDM methods (AHP, TOPSIS)

### Phase 3
- Multi-stakeholder collaboration features
- Mobile app
- Scenario planning and "what-if" analysis

### Phase 4
- 3D visualization
- Drone flight path optimization
- Shelter allocation algorithms

---

**Architecture Version**: 1.0
**Last Updated**: October 2026

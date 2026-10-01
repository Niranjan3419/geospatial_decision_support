# Getting Started - Quick Start Guide

## 5-Minute Setup

### 1. Environment Setup
```bash
# Navigate to project
cd geospatial_decision_support

# Create Python virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Backend will start at: http://localhost:8000
Interactive API docs: http://localhost:8000/docs

### 3. Start Frontend
Open a new terminal:
```bash
cd frontend
python -m http.server 8001
```

Frontend available at: http://localhost:8001/templates/index.html

### 4. Test the System

1. **Prepare test hazard data** (or use sample data in `data/raw/`)
2. **Load hazard layers** via API or upload through UI
3. **Calculate risk index** with default or custom MCDM weights
4. **View map** with risk visualization
5. **Find routes** between start/end points

## Testing Without Real Data

The system can operate in demo mode:

```bash
# Test API without data
curl http://localhost:8000/status

# View API documentation
# Open browser to: http://localhost:8000/docs
```

## Common Commands

### Backend
```bash
# Start with auto-reload (development)
python -m uvicorn app.main:app --reload

# Start production server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Install additional packages
pip install <package_name>
```

### Frontend
```bash
# Python 3 HTTP server
python -m http.server 8001

# Using Node http-server
npm install -g http-server
http-server -p 8001
```

## Project File Layout

```
backend/
  ├── app/main.py              ← FastAPI app entry point
  ├── app/services/            ← Core business logic
  │   ├── hazard_processor.py   ← Load & normalize hazards
  │   ├── mcdm.py               ← Risk calculation
  │   └── routing.py            ← Emergency routing
  └── requirements.txt          ← Python packages

frontend/
  ├── templates/index.html      ← Main web page
  └── static/
      ├── app.js                ← Frontend logic
      └── style.css             ← Styling

data/
  ├── raw/                      ← Your GIS data here
  └── processed/                ← Output results
```

## Key Features to Test

### 1. Hazard Processing
- Load raster (GeoTIFF) or vector (Shapefile) files
- Auto-normalization to 0-1 scale
- Support for flood, landslide, slope data

### 2. MCDM Risk Assessment
- Adjust weights for different hazards
- Real-time risk index calculation
- High-risk zone identification

### 3. Emergency Routing
- Least-risk path finding
- Alternative route suggestions
- Visual route display on map

### 4. Interactive Web UI
- Real-time map visualization
- Slider controls for MCDM weights
- Route design tools

## API Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/status` | GET | Check system status |
| `/risk/calculate` | POST | Compute risk index |
| `/risk/high-risk-locations` | POST | Find high-risk zones |
| `/routing/find-path` | POST | Get optimal emergency route |
| `/routing/alternatives` | POST | Get alternative routes |
| `/docs` | GET | Interactive API documentation |

## Sample API Calls

### Calculate Risk Index
```bash
curl -X POST http://localhost:8000/risk/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "flood": 0.35,
    "landslide": 0.35,
    "slope": 0.20,
    "proximity_settlements": 0.10
  }'
```

### Find Optimal Route
```bash
curl -X POST http://localhost:8000/routing/find-path \
  -H "Content-Type: application/json" \
  -d '{
    "start": [50, 50],
    "end": [150, 150],
    "alternative_count": 3
  }'
```

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall

# Check port 8000 is available
netstat -an | grep 8000
```

### Frontend doesn't load
```bash
# Check HTTP server is running on port 8001
# Clear browser cache
# Check browser console for errors (F12)
```

### API CORS Issues
- Frontend is configured for localhost
- For remote deployment, update CORS settings in `backend/app/main.py`

## Next Steps

1. **Add real data**: Place GeoTIFF/Shapefile in `data/raw/`
2. **Configure weights**: Adjust MCDM weights for your region
3. **Optimize routes**: Test different start/end locations
4. **Export results**: Save risk maps and routes for reports
5. **Integrate feedback**: Refine weights based on stakeholder input

## Documentation

- See [README.md](../README.md) for full documentation
- API documentation at: http://localhost:8000/docs
- Technical details in code docstrings

## Support

For issues or questions:
1. Check API documentation: `/docs` endpoint
2. Review error messages in browser console
3. Check backend logs in terminal
4. Verify data format matches requirements

---

**Happy hacking! 🚀**

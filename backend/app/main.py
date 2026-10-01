"""
FastAPI backend for Geospatial Decision Support System.
Handles hazard analysis, MCDM-based risk assessment, and emergency routing.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
import numpy as np
from typing import Dict, List, Optional, Tuple

try:
    from app.services.hazard_processor import HazardProcessor
    from app.services.mcdm import McdmRiskCalculator, McdmWeights
    from app.services.routing import LeastRiskRouter
except ModuleNotFoundError:
    from services.hazard_processor import HazardProcessor
    from services.mcdm import McdmRiskCalculator, McdmWeights
    from services.routing import LeastRiskRouter


# Initialize FastAPI app
app = FastAPI(
    title="Geospatial Decision Support System",
    description="Multi-hazard risk assessment and emergency routing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
DATA_DIR = Path(__file__).parent.parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)

hazard_processor = HazardProcessor(DATA_DIR)
risk_calculator = None
router = None
current_risk_index = None


# Pydantic models
class HazardSummary(BaseModel):
    """Summary of loaded hazard layers."""
    hazards: Dict[str, Dict]
    message: str


class RiskWeights(BaseModel):
    """Weights for MCDM calculation."""
    flood: float = 0.35
    landslide: float = 0.35
    slope: float = 0.20
    proximity_settlements: float = 0.10


class HighRiskLocations(BaseModel):
    """High-risk location information."""
    count: int
    threshold: float
    message: str


class RouteRequest(BaseModel):
    """Request for route finding."""
    start: Tuple[int, int]
    end: Tuple[int, int]
    alternative_count: int = 3


class RouteResponse(BaseModel):
    """Route response with path and cost."""
    path: List[Tuple[int, int]]
    cost: float
    risk_level: str


# Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Geospatial Decision Support System API",
        "status": "running"
    }


@app.get("/status")
async def status():
    """Get system status."""
    return {
        "hazard_layers_loaded": len(hazard_processor.hazard_layers),
        "risk_index_calculated": current_risk_index is not None,
        "router_ready": router is not None,
        "data_directory": str(DATA_DIR)
    }


@app.post("/hazards/summary")
async def get_hazard_summary() -> HazardSummary:
    """Get summary of loaded hazard layers."""
    summary = hazard_processor.get_hazard_summary()
    return HazardSummary(
        hazards=summary,
        message=f"Loaded {len(summary)} hazard layers"
    )


@app.post("/risk/calculate")
async def calculate_risk_index(weights: Optional[RiskWeights] = None) -> JSONResponse:
    """
    Calculate multi-hazard risk index using MCDM.
    
    Requires hazard layers to be loaded first.
    """
    global risk_calculator, current_risk_index, router
    
    if not hazard_processor.hazard_layers:
        raise HTTPException(
            status_code=400,
            detail="No hazard layers loaded. Upload hazard data first."
        )
    
    try:
        # Create MCDM calculator
        if weights:
            w = McdmWeights(
                flood=weights.flood,
                landslide=weights.landslide,
                slope=weights.slope,
                proximity_settlements=weights.proximity_settlements
            )
            risk_calculator = McdmRiskCalculator(w)
        else:
            risk_calculator = McdmRiskCalculator()
        
        # Prepare hazard layers (assuming normalized data)
        hazard_layers = {}
        for hazard_type, data in hazard_processor.hazard_layers.items():
            if isinstance(data, dict) and 'data' in data:
                hazard_layers[hazard_type] = data['data']
        
        if not hazard_layers:
            raise ValueError("No valid hazard data found")
        
        # Calculate risk index
        current_risk_index = risk_calculator.calculate_risk_index(hazard_layers)
        
        # Initialize router
        router = LeastRiskRouter(current_risk_index)
        router.create_road_graph()
        
        return JSONResponse({
            "status": "success",
            "message": "Risk index calculated",
            "risk_shape": current_risk_index.shape,
            "risk_min": float(np.nanmin(current_risk_index)),
            "risk_max": float(np.nanmax(current_risk_index)),
            "risk_mean": float(np.nanmean(current_risk_index))
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/risk/high-risk-locations")
async def identify_high_risk(threshold: float = 0.6) -> HighRiskLocations:
    """Identify high-risk locations in the risk index."""
    if current_risk_index is None:
        raise HTTPException(
            status_code=400,
            detail="Risk index not calculated. Run /risk/calculate first."
        )
    
    count, coords = risk_calculator.identify_high_risk_locations(
        current_risk_index,
        threshold=threshold
    )
    
    return HighRiskLocations(
        count=int(count),
        threshold=threshold,
        message=f"Found {count} high-risk locations above threshold {threshold}"
    )


@app.post("/routing/find-path")
async def find_emergency_route(request: RouteRequest) -> RouteResponse:
    """Find least-risk emergency route."""
    if router is None:
        raise HTTPException(
            status_code=400,
            detail="Router not initialized. Calculate risk index first."
        )
    
    try:
        path, cost = router.find_least_risk_path(request.start, request.end)
        
        if not path:
            raise HTTPException(
                status_code=404,
                detail="No path found between start and end points"
            )
        
        # Categorize risk level
        avg_risk = cost / len(path) if path else 0
        if avg_risk < 0.3:
            risk_level = "Low"
        elif avg_risk < 0.6:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return RouteResponse(
            path=path,
            cost=float(cost),
            risk_level=risk_level
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/routing/alternatives")
async def find_alternative_routes(request: RouteRequest) -> JSONResponse:
    """Find k alternative least-risk routes."""
    if router is None:
        raise HTTPException(
            status_code=400,
            detail="Router not initialized. Calculate risk index first."
        )
    
    try:
        routes = router.get_alternative_routes(
            request.start,
            request.end,
            k=request.alternative_count
        )
        
        return JSONResponse({
            "status": "success",
            "routes_found": len(routes),
            "routes": [
                {
                    "path": path,
                    "cost": float(cost),
                    "length": len(path)
                }
                for path, cost in routes
            ]
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

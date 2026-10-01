"""
Hazard layer processing service for flood, landslide, and slope analysis.
"""
import numpy as np
import geopandas as gpd
import rasterio
from pathlib import Path
from typing import Dict, Tuple, Optional


class HazardProcessor:
    """Process and normalize individual hazard layers."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.hazard_layers = {}
    
    def load_raster_hazard(self, file_path: Path, hazard_type: str) -> np.ndarray:
        """
        Load a raster file (GeoTIFF) for a hazard layer.
        
        Args:
            file_path: Path to raster file
            hazard_type: Type of hazard ('flood', 'landslide', 'slope')
        
        Returns:
            Numpy array of hazard data
        """
        with rasterio.open(file_path) as src:
            data = src.read(1)
            self.hazard_layers[hazard_type] = {
                'data': data,
                'profile': src.profile,
                'bounds': src.bounds
            }
        return data
    
    def normalize_hazard(self, hazard_data: np.ndarray, method: str = 'minmax') -> np.ndarray:
        """
        Normalize hazard layer to 0-1 scale.
        
        Args:
            hazard_data: Raw hazard data
            method: Normalization method ('minmax' or 'zscore')
        
        Returns:
            Normalized array (0-1)
        """
        # Handle nodata values
        valid_mask = hazard_data != -9999
        
        if method == 'minmax':
            vmin = np.nanmin(hazard_data[valid_mask])
            vmax = np.nanmax(hazard_data[valid_mask])
            if vmax > vmin:
                normalized = (hazard_data - vmin) / (vmax - vmin)
            else:
                normalized = hazard_data.copy()
        else:  # zscore
            mean = np.nanmean(hazard_data[valid_mask])
            std = np.nanstd(hazard_data[valid_mask])
            normalized = (hazard_data - mean) / (std + 1e-8)
            normalized = (normalized + 3) / 6  # Scale to [0, 1]
            normalized = np.clip(normalized, 0, 1)
        
        # Preserve nodata
        normalized[~valid_mask] = np.nan
        return normalized
    
    def load_vector_hazard(self, file_path: Path, hazard_type: str) -> gpd.GeoDataFrame:
        """
        Load vector file (Shapefile/GeoJSON) for hazard zones.
        
        Args:
            file_path: Path to vector file
            hazard_type: Type of hazard
        
        Returns:
            GeoDataFrame with hazard zones
        """
        gdf = gpd.read_file(file_path)
        self.hazard_layers[hazard_type] = gdf
        return gdf
    
    def get_hazard_summary(self) -> Dict:
        """Return summary of loaded hazard layers."""
        return {
            hazard: {
                'type': 'raster' if isinstance(data, dict) else 'vector',
                'loaded': True
            }
            for hazard, data in self.hazard_layers.items()
        }

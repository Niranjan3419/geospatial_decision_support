"""
Multi-Criteria Decision Making (MCDM) service for risk index calculation.
"""
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class McdmWeights:
    """Weights for different criteria."""
    flood: float = 0.35
    landslide: float = 0.35
    slope: float = 0.20
    proximity_settlements: float = 0.10
    

class McdmRiskCalculator:
    """Calculate multi-hazard risk index using weighted criteria."""
    
    def __init__(self, weights: McdmWeights = None):
        """
        Initialize MCDM calculator.
        
        Args:
            weights: Weights for each criterion (defaults to equal-ish distribution)
        """
        self.weights = weights or McdmWeights()
        self._validate_weights()
    
    def _validate_weights(self):
        """Ensure weights sum to 1.0."""
        total = (self.weights.flood + self.weights.landslide + 
                self.weights.slope + self.weights.proximity_settlements)
        if not np.isclose(total, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def calculate_risk_index(self, hazard_layers: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Calculate composite risk index from normalized hazard layers.
        
        Args:
            hazard_layers: Dictionary of hazard type -> normalized array
        
        Returns:
            Risk index array (0-1)
        """
        risk_index = np.zeros_like(hazard_layers.get('flood', None), dtype=float)
        
        if 'flood' in hazard_layers:
            risk_index += self.weights.flood * hazard_layers['flood']
        
        if 'landslide' in hazard_layers:
            risk_index += self.weights.landslide * hazard_layers['landslide']
        
        if 'slope' in hazard_layers:
            risk_index += self.weights.slope * hazard_layers['slope']
        
        if 'proximity_settlements' in hazard_layers:
            risk_index += self.weights.proximity_settlements * hazard_layers['proximity_settlements']
        
        # Clip to [0, 1]
        risk_index = np.clip(risk_index, 0, 1)
        return risk_index
    
    def identify_high_risk_locations(self, risk_index: np.ndarray, 
                                    threshold: float = 0.6) -> Tuple[int, int]:
        """
        Identify high-risk locations in risk index.
        
        Args:
            risk_index: Risk index array
            threshold: Risk threshold (default 0.6)
        
        Returns:
            Count of high-risk pixels and their coordinates
        """
        high_risk_mask = risk_index >= threshold
        high_risk_count = np.sum(high_risk_mask)
        high_risk_coords = np.argwhere(high_risk_mask)
        
        return high_risk_count, high_risk_coords
    
    def update_weights(self, new_weights: Dict[str, float]):
        """
        Update MCDM weights dynamically.
        
        Args:
            new_weights: Dictionary with new weight values
        """
        for key, value in new_weights.items():
            if hasattr(self.weights, key):
                setattr(self.weights, key, value)
        self._validate_weights()

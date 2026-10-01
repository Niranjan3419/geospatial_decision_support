"""
Emergency route finding service using least-risk pathfinding.
"""
import numpy as np
from typing import List, Tuple, Optional
import networkx as nx
from heapq import heappush, heappop


class LeastRiskRouter:
    """Find least-risk emergency routes considering hazard layers."""
    
    def __init__(self, risk_index: np.ndarray, resolution: float = 10.0):
        """
        Initialize router with risk index grid.
        
        Args:
            risk_index: Risk index array (0-1)
            resolution: Grid cell resolution in meters
        """
        self.risk_index = risk_index
        self.resolution = resolution
        self.graph = None
    
    def create_road_graph(self, road_network: Optional[np.ndarray] = None):
        """
        Create graph from road network or regular grid.
        
        Args:
            road_network: Binary array where 1=road, 0=no road.
                         If None, creates full grid.
        """
        h, w = self.risk_index.shape
        
        if road_network is None:
            # Use full grid
            road_network = np.ones_like(self.risk_index, dtype=bool)
        
        self.graph = nx.Graph()
        
        # Add nodes for valid cells
        for i in range(h):
            for j in range(w):
                if road_network[i, j]:
                    self.graph.add_node((i, j))
        
        # Add edges with weights based on risk
        for i in range(h):
            for j in range(w):
                if not road_network[i, j]:
                    continue
                
                # 8-connectivity
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1),
                              (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    ni, nj = i + di, j + dj
                    
                    if 0 <= ni < h and 0 <= nj < w and road_network[ni, nj]:
                        # Distance weight (Manhattan or Euclidean based on direction)
                        if di != 0 and dj != 0:
                            dist = self.resolution * np.sqrt(2)
                        else:
                            dist = self.resolution
                        
                        # Risk weight (average of both cells)
                        avg_risk = (self.risk_index[i, j] + self.risk_index[ni, nj]) / 2
                        
                        # Combined cost: distance + risk penalty
                        # Higher risk = longer effective "distance"
                        cost = dist * (1 + avg_risk)
                        
                        self.graph.add_edge((i, j), (ni, nj), weight=cost)
    
    def find_least_risk_path(self, start: Tuple[int, int], 
                            end: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], float]:
        """
        Find least-risk path between start and end points.
        
        Args:
            start: Start cell coordinates (row, col)
            end: End cell coordinates (row, col)
        
        Returns:
            Path (list of coordinates) and total cost
        """
        if self.graph is None:
            self.create_road_graph()
        
        try:
            path = nx.shortest_path(self.graph, start, end, weight='weight')
            cost = nx.shortest_path_length(self.graph, start, end, weight='weight')
            return path, cost
        except nx.NetworkXNoPath:
            return [], float('inf')
    
    def get_alternative_routes(self, start: Tuple[int, int], 
                              end: Tuple[int, int], k: int = 3) -> List[Tuple[List, float]]:
        """
        Get k alternative least-risk routes.
        
        Args:
            start: Start coordinates
            end: End coordinates
            k: Number of alternative routes
        
        Returns:
            List of (path, cost) tuples
        """
        if self.graph is None:
            self.create_road_graph()
        
        routes = []
        try:
            # Find k shortest paths
            for path in nx.shortest_simple_paths(self.graph, start, end, weight='weight'):
                if len(routes) >= k:
                    break
                cost = sum(
                    self.graph[path[i]][path[i+1]]['weight'] 
                    for i in range(len(path) - 1)
                )
                routes.append((path, cost))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            pass
        
        return routes

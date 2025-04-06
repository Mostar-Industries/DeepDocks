"""
DeepCAL++ Utilities Module
This module provides utility functions for the core engine
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Union, Optional
import os
import json

def build_pairwise_weights(matrix: List[List[float]]) -> List[float]:
    """
    Build weights from a pairwise comparison matrix using the AHP method
    
    Args:
        matrix: Pairwise comparison matrix
        
    Returns:
        List of weights
    """
    # Convert to numpy array
    arr = np.array(matrix, dtype=float)
    
    # Calculate column sums
    column_sums = arr.sum(axis=0)
    
    # Normalize the matrix
    normalized = arr / column_sums
    
    # Calculate weights as row averages
    weights = normalized.mean(axis=1)
    
    # Normalize weights to sum to 1
    weights = weights / weights.sum()
    
    return weights.tolist()

def grey_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize data using Grey Relational Analysis
    
    Args:
        df: DataFrame with raw data
        
    Returns:
        DataFrame with normalized data
    """
    # Create a copy to avoid modifying the original
    normalized_df = df.copy()
    
    # Normalize cost and time (lower is better)
    for col in ['cost', 'time']:
        if col in df.columns:
            max_val = df[col].max()
            min_val = df[col].min()
            # Grey normalization formula for cost-type criteria
            normalized_df[col] = (max_val - df[col]) / (max_val - min_val + 1e-9)
    
    # Normalize reliability (higher is better)
    if 'reliability' in df.columns:
        max_val = df['reliability'].max()
        min_val = df['reliability'].min()
        # Grey normalization formula for benefit-type criteria
        normalized_df['reliability'] = (df['reliability'] - min_val) / (max_val - min_val + 1e-9)
    
    # Handle tracking (binary)
    if 'tracking' in df.columns:
        normalized_df['tracking'] = df['tracking'].astype(float)
    
    return normalized_df

def neutrosophic_topsis(df: pd.DataFrame, weights: List[float], 
                        benefit_criteria: List[str] = ['reliability', 'tracking'],
                        cost_criteria: List[str] = ['cost', 'time']) -> List[Dict[str, Any]]:
    """
    Perform Neutrosophic TOPSIS analysis
    
    Args:
        df: DataFrame with normalized data
        weights: List of weights for each criterion
        benefit_criteria: List of benefit criteria (higher is better)
        cost_criteria: List of cost criteria (lower is better)
        
    Returns:
        List of dictionaries with ranking results
    """
    # Extract the criteria columns
    criteria = benefit_criteria + cost_criteria
    available_criteria = [c for c in criteria if c in df.columns]
    
    # Create the decision matrix
    decision_matrix = df[available_criteria].values
    
    # Adjust weights to match available criteria
    adjusted_weights = []
    for i, criterion in enumerate(criteria):
        if criterion in available_criteria:
            adjusted_weights.append(weights[i])
    
    # Normalize weights to sum to 1
    adjusted_weights = np.array(adjusted_weights) / sum(adjusted_weights)
    
    # Calculate weighted normalized decision matrix
    weighted_matrix = decision_matrix * adjusted_weights
    
    # Determine ideal and anti-ideal solutions
    ideal = np.zeros(len(available_criteria))
    anti_ideal = np.zeros(len(available_criteria))
    
    for i, criterion in enumerate(available_criteria):
        if criterion in benefit_criteria:
            ideal[i] = np.max(weighted_matrix[:, i])
            anti_ideal[i] = np.min(weighted_matrix[:, i])
        else:  # Cost criterion
            ideal[i] = np.min(weighted_matrix[:, i])
            anti_ideal[i] = np.max(weighted_matrix[:, i])
    
    # Calculate separation measures
    s_plus = np.sqrt(np.sum((weighted_matrix - ideal)**2, axis=1))
    s_minus = np.sqrt(np.sum((weighted_matrix - anti_ideal)**2, axis=1))
    
    # Calculate relative closeness to the ideal solution
    closeness = s_minus / (s_plus + s_minus + 1e-9)
    
    # Create results
    results = []
    for i, row in df.iterrows():
        # Calculate normalized factor values (0-1 scale)
        cost_factor = 0.0
        time_factor = 0.0
        reliability_factor = 0.0
        
        if 'cost' in df.columns:
            cost_factor = (row['cost'] - df['cost'].min()) / (df['cost'].max() - df['cost'].min() + 1e-9)
        
        if 'time' in df.columns:
            time_factor = (row['time'] - df['time'].min()) / (df['time'].max() - df['time'].min() + 1e-9)
        
        if 'reliability' in df.columns:
            reliability_factor = (row['reliability'] - df['reliability'].min()) / (df['reliability'].max() - df['reliability'].min() + 1e-9)
        
        result = {
            "id": str(row.get('id', f"f{i+1}")),
            "name": row['name'],
            "score": float(closeness[i]),
            "cost": float(row.get('cost', 0)),
            "deliveryTime": float(row.get('time', 0)),
            "reliability": float(row.get('reliability', 0) * 100),  # Convert to percentage
            "hasTracking": bool(row.get('tracking', False)),
            "costFactor": float(cost_factor),
            "timeFactor": float(time_factor),
            "reliabilityFactor": float(reliability_factor),
        }
        
        results.append(result)
    
    # Sort by score (descending)
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    
    # Assign ranks
    for i, result in enumerate(results):
        result["rank"] = i + 1
    
    return results

def adjust_for_urgency(weights: List[float], urgency: str) -> List[float]:
    """
    Adjust weights based on urgency level
    
    Args:
        weights: Original weights
        urgency: Urgency level (standard, express, rush)
        
    Returns:
        Adjusted weights
    """
    adjusted_weights = weights.copy()
    
    if urgency == "express":
        # Increase weight for time, decrease for cost
        time_idx = 1  # Assuming time is the second criterion
        cost_idx = 0  # Assuming cost is the first criterion
        
        # Increase time weight by 50%
        time_boost = adjusted_weights[time_idx] * 0.5
        adjusted_weights[time_idx] += time_boost
        
        # Decrease cost weight to compensate
        adjusted_weights[cost_idx] -= time_boost
        
    elif urgency == "rush":
        # Significantly increase weight for time, significantly decrease for cost
        time_idx = 1  # Assuming time is the second criterion
        cost_idx = 0  # Assuming cost is the first criterion
        
        # Increase time weight by 100%
        time_boost = adjusted_weights[time_idx] * 1.0
        adjusted_weights[time_idx] += time_boost
        
        # Decrease cost weight to compensate
        adjusted_weights[cost_idx] -= time_boost
    
    # Ensure weights are non-negative
    adjusted_weights = [max(0, w) for w in adjusted_weights]
    
    # Normalize weights to sum to 1
    total = sum(adjusted_weights)
    adjusted_weights = [w / total for w in adjusted_weights]
    
    return adjusted_weights

def load_forwarders_for(origin: str, destination: str, cargo_type: str = "general") -> List[Dict[str, Any]]:
    """
    Load forwarders for a specific route from the database or file
    
    Args:
        origin: Origin location
        destination: Destination location
        cargo_type: Type of cargo
        
    Returns:
        List of forwarder dictionaries
    """
    try:
        # First try to load from a JSON file (for testing/development)
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'forwarders.json')
        
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                all_forwarders = json.load(f)
            
            # Filter forwarders for the specific route
            forwarders = []
            for forwarder in all_forwarders:
                routes = forwarder.get('routes', [])
                for route in routes:
                    if route.get('origin') == origin and route.get('destination') == destination:
                        # Create a copy of the forwarder with route-specific data
                        forwarder_copy = forwarder.copy()
                        forwarder_copy.update(route)
                        forwarders.append(forwarder_copy)
            
            return forwarders
        
        # If file doesn't exist, return empty list (will use mock data)
        return []
        
    except Exception as e:
        print(f"Error loading forwarders: {e}")
        return []


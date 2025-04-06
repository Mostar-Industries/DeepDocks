"""
DeepCAL++ Core Engine (Refined Unified Version)
Supports Classic, Neutrosophic, and Grey TOPSIS with base data integration
"""
import os
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Union, Tuple, Optional
import logging
from ..data.data_mirror import get_data_mirror, get_base_forwarders, get_base_routes, get_base_rate_cards, get_training_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("deepcal_core")

# --------------------------
# Input Preprocessor
# --------------------------

def process_logistics_data(forwarders: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Process the input forwarder data into a format suitable for analysis
    
    Args:
        forwarders: List of dictionaries containing forwarder data
        
    Returns:
        Processed DataFrame ready for analysis
    """
    # Convert to DataFrame
    df = pd.DataFrame(forwarders)
    
    # Convert tracking boolean to numeric
    if 'tracking' in df.columns:
        df['tracking'] = df['tracking'].astype(int)
    
    # Ensure all numeric columns are float
    numeric_cols = ['cost', 'time', 'reliability']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(float)
    
    return df

# --------------------------
# Data Integration
# --------------------------

def load_forwarders_for_route(origin: str, destination: str, cargo_type: str = "general", 
                             use_supabase_data: bool = True, supabase_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Load forwarders for a specific route, integrating Supabase and base data
    
    Args:
        origin: Origin location
        destination: Destination location
        cargo_type: Type of cargo
        use_supabase_data: Whether to use Supabase data if available
        supabase_data: Optional Supabase data to use
        
    Returns:
        List of forwarder dictionaries
    """
    forwarders = []
    
    # Step 1: Try to use Supabase data if available and requested
    if use_supabase_data and supabase_data:
        try:
            # Extract route information
            routes = supabase_data.get('routes', [])
            route_id = None
            
            for route in routes:
                if route.get('origin_country') == origin and route.get('destination_country') == destination:
                    route_id = route.get('id')
                    break
            
            # If route found, get rate cards for this route
            if route_id:
                rate_cards = supabase_data.get('rate_cards', [])
                forwarder_data = supabase_data.get('forwarders', [])
                
                # Create a dictionary of forwarders by ID for easy lookup
                forwarders_dict = {f.get('id'): f for f in forwarder_data}
                
                # Process rate cards for this route
                for card in rate_cards:
                    if card.get('route_id') == route_id and card.get('cargo_type') == cargo_type:
                        forwarder_id = card.get('forwarder_id')
                        if forwarder_id in forwarders_dict:
                            forwarder = forwarders_dict[forwarder_id].copy()
                            
                            # Add rate card data to forwarder
                            forwarder['cost'] = card.get('base_cost', 0)
                            
                            # Add route data
                            for route_item in routes:
                                if route_item.get('id') == route_id:
                                    forwarder['time'] = route_item.get('typical_transit_days', 15)
                                    break
                            
                            # Add tracking information if available
                            forwarder_services = supabase_data.get('forwarder_services', [])
                            for service in forwarder_services:
                                if service.get('forwarder_id') == forwarder_id:
                                    forwarder['tracking'] = service.get('has_tracking', False)
                                    break
                            
                            # Add reliability from performance analytics if available
                            performance_analytics = supabase_data.get('performance_analytics', [])
                            for analytics in performance_analytics:
                                if analytics.get('forwarder_id') == forwarder_id and analytics.get('route_id') == route_id:
                                    forwarder['reliability'] = analytics.get('on_time_rate', 0.8)
                                    break
                            
                            # Ensure reliability exists (default if not found)
                            if 'reliability' not in forwarder:
                                forwarder['reliability'] = 0.8
                            
                            # Ensure tracking exists (default if not found)
                            if 'tracking' not in forwarder:
                                forwarder['tracking'] = False
                            
                            forwarders.append(forwarder)
        except Exception as e:
            logger.error(f"Error processing Supabase data: {e}")
    
    # Step 2: If no forwarders found from Supabase, use base data
    if not forwarders:
        try:
            # Get base data
            base_forwarders = get_base_forwarders()
            base_routes = get_base_routes()
            base_rate_cards = get_base_rate_cards()
            
            # Find route ID
            route_id = None
            for route in base_routes:
                if route.get('origin_country') == origin and route.get('destination_country') == destination:
                    route_id = route.get('id')
                    break
            
            # If route found, get rate cards for this route
            if route_id:
                # Create a dictionary of forwarders by ID for easy lookup
                forwarders_dict = {f.get('id'): f for f in base_forwarders}
                
                # Process rate cards for this route
                for card in base_rate_cards:
                    if card.get('route_id') == route_id and card.get('cargo_type') == cargo_type:
                        forwarder_id = card.get('forwarder_id')
                        if forwarder_id in forwarders_dict:
                            forwarder = forwarders_dict[forwarder_id].copy()
                            
                            # Add rate card data to forwarder
                            forwarder['cost'] = card.get('base_cost', 0)
                            
                            # Add route data
                            for route_item in base_routes:
                                if route_item.get('id') == route_id:
                                    forwarder['time'] = route_item.get('typical_transit_days', 15)
                                    break
                            
                            # Ensure reliability exists (default if not found)
                            if 'reliability' not in forwarder:
                                forwarder['reliability'] = 0.8
                            
                            # Ensure tracking exists (default if not found)
                            if 'tracking' not in forwarder:
                                forwarder['tracking'] = False
                            
                            forwarders.append(forwarder)
        except Exception as e:
            logger.error(f"Error processing base data: {e}")
    
    # Step 3: If still no forwarders found, use fallback data
    if not forwarders:
        logger.warning(f"No forwarders found for route {origin} to {destination}. Using fallback data.")
        forwarders = generate_fallback_forwarders(origin, destination)
    
    return forwarders

def generate_fallback_forwarders(origin: str, destination: str) -> List[Dict[str, Any]]:
    """
    Generate fallback forwarders when no data is available
    
    Args:
        origin: Origin location
        destination: Destination location
        
    Returns:
        List of fallback forwarder dictionaries
    """
    # Create base forwarders with different characteristics
    forwarders = [
        {
            "id": "f1",
            "name": "AfricaLogistics",
            "cost": 1200,
            "time": 14,
            "reliability": 0.85,
            "tracking": True
        },
        {
            "id": "f2",
            "name": "GlobalFreight",
            "cost": 950,
            "time": 18,
            "reliability": 0.78,
            "tracking": False
        },
        {
            "id": "f3",
            "name": "ExpressShip",
            "cost": 1450,
            "time": 10,
            "reliability": 0.92,
            "tracking": True
        },
        {
            "id": "f4",
            "name": "TransAfrica",
            "cost": 1100,
            "time": 15,
            "reliability": 0.82,
            "tracking": True
        },
        {
            "id": "f5",
            "name": "FastCargo",
            "cost": 1350,
            "time": 12,
            "reliability": 0.88,
            "tracking": False
        }
    ]
    
    return forwarders

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

# --------------------------
# Neutrosophic Math
# --------------------------

def neutrosophic_transform(x: float, uncertainty: float = 0.1) -> Tuple[float, float, float]:
    """
    Transform a crisp value into a neutrosophic triplet (T, I, F)
    
    Args:
        x: Crisp value between 0 and 1
        uncertainty: Uncertainty level
        
    Returns:
        Neutrosophic triplet (Truth, Indeterminacy, Falsity)
    """
    T = max(min(x, 1.0), 0.0)
    I = min(uncertainty, 1 - T)
    F = max(0, 1 - T - I)
    return T, I, F

def neutrosophic_score(triplet: Tuple[float, float, float]) -> float:
    """
    Calculate score of a neutrosophic triplet
    
    Args:
        triplet: Neutrosophic triplet (T, I, F)
        
    Returns:
        Score value
    """
    T, I, F = triplet
    return T - F - 0.5 * I

# --------------------------
# Grey Math
# --------------------------

def grey_transform(x: float, delta: float = 0.2) -> Tuple[float, float]:
    """
    Transform a crisp value into a grey interval
    
    Args:
        x: Crisp value between 0 and 1
        delta: Uncertainty range
        
    Returns:
        Grey interval (lower, upper)
    """
    return (max(x - delta, 0), min(x + delta, 1))

def grey_score(interval: Tuple[float, float]) -> float:
    """
    Calculate score of a grey interval
    
    Args:
        interval: Grey interval (lower, upper)
        
    Returns:
        Score value
    """
    return sum(interval) / 2

# --------------------------
# TOPSIS Framework
# --------------------------

def normalize_matrix(X: np.ndarray) -> np.ndarray:
    """
    Normalize decision matrix using vector normalization
    
    Args:
        X: Decision matrix
        
    Returns:
        Normalized matrix
    """
    norms = np.linalg.norm(X, axis=0)
    norms[norms == 0] = 1e-10
    return X / norms

def determine_ideal(X: np.ndarray, types: List[str]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Determine ideal and anti-ideal solutions
    
    Args:
        X: Weighted normalized matrix
        types: List of criteria types ('benefit' or 'cost')
        
    Returns:
        Tuple of ideal and anti-ideal solutions
    """
    ideal, anti = [], []
    for j, t in enumerate(types):
        col = X[:, j]
        ideal.append(np.max(col) if t == 'benefit' else np.min(col))
        anti.append(np.min(col) if t == 'benefit' else np.max(col))
    return np.array(ideal), np.array(anti)

def calculate_separation(X: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """
    Calculate separation measures from reference point
    
    Args:
        X: Weighted normalized matrix
        ref: Reference point (ideal or anti-ideal)
        
    Returns:
        Array of separation measures
    """
    return np.sqrt(np.sum((X - ref) ** 2, axis=1))

def criterion_contributions(x: np.ndarray, ideal: np.ndarray, anti: np.ndarray) -> List[float]:
    """
    Calculate contribution of each criterion to the final score
    
    Args:
        x: Row of weighted normalized matrix
        ideal: Ideal solution
        anti: Anti-ideal solution
        
    Returns:
        List of contribution values
    """
    result = []
    for j in range(len(x)):
        d_pos = (x[j] - ideal[j]) ** 2
        d_neg = (x[j] - anti[j]) ** 2
        contrib = d_neg / (d_neg + d_pos) if (d_pos + d_neg) > 0 else 0
        result.append(float(contrib))
    return result

# --------------------------
# Main Ranking Function
# --------------------------

def run_topsis(
    df: pd.DataFrame,
    weights: List[float],
    criteria_types: List[str],
    use_neutrosophic: bool = False,
    use_grey: bool = False,
    analysis_depth: int = 3,
    training_data: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Run TOPSIS analysis with optional neutrosophic or grey extensions
    
    Args:
        df: DataFrame with forwarder data
        weights: List of criteria weights
        criteria_types: List of criteria types ('benefit' or 'cost')
        use_neutrosophic: Whether to use neutrosophic extension
        use_grey: Whether to use grey extension
        analysis_depth: Level of detail in results (1-5)
        training_data: Optional training data to enhance analysis
        
    Returns:
        List of ranked results
    """
    columns = ['cost', 'time', 'reliability']
    if 'tracking' in df.columns:
        columns.append('tracking')

    matrix = df[columns].values
    norm_matrix = normalize_matrix(matrix)
    weights = np.array(weights[:len(columns)])
    weighted = norm_matrix * weights

    # Apply training data adjustments if available
    if training_data and 'weight_adjustments' in training_data:
        weight_adjustments = training_data['weight_adjustments']
        for i, col in enumerate(columns):
            if col in weight_adjustments and i < len(weights):
                weights[i] *= weight_adjustments[col]
        
        # Renormalize weights
        weights = weights / np.sum(weights)
        weighted = norm_matrix * weights

    ideal, anti = determine_ideal(weighted, criteria_types[:len(columns)])
    s_plus = calculate_separation(weighted, ideal)
    s_minus = calculate_separation(weighted, anti)

    base_scores = s_minus / (s_plus + s_minus + 1e-9)

    # Apply logic extension
    if use_neutrosophic:
        # Apply uncertainty from training data if available
        uncertainty = 0.1
        if training_data and 'uncertainty' in training_data:
            uncertainty = training_data['uncertainty']
        
        scores = [neutrosophic_score(neutrosophic_transform(s, uncertainty)) for s in base_scores]
    elif use_grey:
        # Apply delta from training data if available
        delta = 0.2
        if training_data and 'grey_delta' in training_data:
            delta = training_data['grey_delta']
            
        scores = [grey_score(grey_transform(s, delta)) for s in base_scores]
    else:
        scores = base_scores

    ranked = np.argsort(scores)[::-1]
    results = []

    for rank, i in enumerate(ranked, 1):
        row = df.iloc[i]
        entry = {
            "id": str(row.get('id', f"f{i+1}")),
            "name": row.get("name", f"F{i+1}"),
            "rank": rank,
            "score": float(scores[i]),
        }
        if analysis_depth >= 2:
            for idx, col in enumerate(columns):
                if col == 'cost':
                    entry["costFactor"] = float(norm_matrix[i, idx])
                elif col == 'time':
                    entry["timeFactor"] = float(norm_matrix[i, idx])
                elif col == 'reliability':
                    entry["reliabilityFactor"] = float(norm_matrix[i, idx])
                elif col == 'tracking':
                    entry["hasTracking"] = bool(row[col])
        if analysis_depth >= 3:
            entry["cost"] = float(row.get('cost', 0))
            entry["deliveryTime"] = float(row.get('time', 0))
            entry["reliability"] = float(row.get('reliability', 0) * 100)  # Convert to percentage
            entry["hasTracking"] = bool(row.get('tracking', False))
        if analysis_depth >= 4:
            entry["separation_ideal"] = float(s_plus[i])
            entry["separation_negative"] = float(s_minus[i])
            entry["criterionContributions"] = criterion_contributions(weighted[i], ideal, anti)
            # Add commentary
            entry["commentary"] = generate_forwarder_commentary(entry, df.to_dict('records'))
        
        # Apply training data adjustments to final scores if available
        if training_data and 'forwarder_adjustments' in training_data:
            forwarder_id = entry["id"]
            if forwarder_id in training_data['forwarder_adjustments']:
                adjustment = training_data['forwarder_adjustments'][forwarder_id]
                entry["score"] = min(1.0, max(0.0, entry["score"] * adjustment))
        
        results.append(entry)

    # Re-sort after potential training data adjustments
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    
    # Reassign ranks
    for rank, result in enumerate(results, 1):
        result["rank"] = rank

    return results

def run_neutrosophic_analysis(
    forwarders: List[Dict[str, Any]], 
    weights: List[float] = None,
    urgency: str = "standard",
    analysis_depth: int = 5,
    criteria_types: List[str] = None,
    supabase_data: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Run neutrosophic analysis combining Grey Systems and N-TOPSIS
    
    Args:
        forwarders: List of dictionaries containing forwarder data
        weights: Optional custom weight vector for criteria
        urgency: Urgency level (standard, express, rush)
        analysis_depth: Level of analysis detail (1-5)
        criteria_types: List of criteria types ('benefit' or 'cost')
        supabase_data: Optional Supabase data to enhance analysis
        
    Returns:
        List of dictionaries containing ranked results
    """
    # Define default weights if not provided
    if weights is None:
        # Default weights: cost (40%), time (30%), reliability (20%), tracking (10%)
        weights = [0.4, 0.3, 0.2, 0.1]
    
    # Process the data
    df = process_logistics_data(forwarders)
    
    # Adjust weights based on urgency
    adjusted_weights = adjust_for_urgency(weights, urgency)
    
    # Define criteria types if not provided
    if criteria_types is None:
        criteria_types = ['cost', 'cost', 'benefit', 'benefit']
    
    # Get training data
    training_data = get_training_data()
    
    # Run TOPSIS with neutrosophic extension
    results = run_topsis(
        df, 
        adjusted_weights, 
        criteria_types, 
        use_neutrosophic=True, 
        use_grey=False, 
        analysis_depth=analysis_depth,
        training_data=training_data
    )
    
    # Add sensitivity analysis if analysis depth is highest
    if analysis_depth >= 5:
        for result in results:
            result["sensitivityAnalysis"] = {
                "weightChanges": [
                    "Cost: +10%",
                    "Cost: -10%",
                    "Time: +10%",
                    "Time: -10%",
                    "Reliability: +10%",
                    "Reliability: -10%"
                ],
                "scoreChanges": calculate_sensitivity_changes(result, adjusted_weights)
            }
    
    return results

def generate_forwarder_commentary(result: Dict[str, Any], forwarders: List[Dict[str, Any]]) -> str:
    """
    Generate commentary for a specific forwarder
    
    Args:
        result: Result dictionary for a forwarder
        forwarders: List of all forwarders
        
    Returns:
        Commentary string
    """
    commentaries = [
        f"{result['name']} offers a balanced approach with {result['reliability']:.0f}% reliability and {result['deliveryTime']} day delivery.",
        f"{result['name']} is particularly strong in {get_strength(result)}.",
        f"{result['name']} {result['hasTracking'] and 'provides real-time tracking capabilities' or 'does not offer tracking services'} for this route.",
        f"{result['name']} is {result['rank'] == 1 and 'the top-ranked option' or f'ranked #{result['rank']}'} based on your shipment requirements."
    ]
    
    # Select 2 random commentaries
    selected = np.random.choice(commentaries, size=2, replace=False)
    
    return " ".join(selected)

def get_strength(result: Dict[str, Any]) -> str:
    """
    Determine the main strength of a forwarder
    
    Args:
        result: Result dictionary for a forwarder
        
    Returns:
        Strength description
    """
    if result["costFactor"] < 0.4:
        return "cost efficiency"
    elif result["timeFactor"] < 0.4:
        return "delivery speed"
    elif result["reliabilityFactor"] > 0.7:
        return "reliability"
    else:
        return "overall balance"

def calculate_sensitivity_changes(result: Dict[str, Any], weights: List[float]) -> List[float]:
    """
    Calculate sensitivity changes for a forwarder
    
    Args:
        result: Result dictionary for a forwarder
        weights: Current weights
        
    Returns:
        List of percentage changes in score
    """
    original_score = result["score"]
    changes = []
    
    # Cost +10%
    new_weights = weights.copy()
    new_weights[0] *= 1.1
    new_weights = [w / sum(new_weights) for w in new_weights]
    new_score = calculate_new_score(result, new_weights)
    changes.append(((new_score - original_score) / original_score) * 100)
    
    # Cost -10%
    new_weights = weights.copy()
    new_weights[0] *= 0.9
    new_weights = [w / sum(new_weights) for w in new_weights]
    new_score = calculate_new_score(result, new_weights)
    changes.append(((new_score - original_score) / original_score) * 100)
    
    # Time +10%
    new_weights = weights.copy()
    new_weights[1] *= 1.1
    new_weights = [w / sum(new_weights) for w in new_weights]
    new_score = calculate_new_score(result, new_weights)
    changes.append(((new_score - original_score) / original_score) * 100)
    
    # Time -10%
    new_weights = weights.copy()
    new_weights[1] *= 0.9
    new_weights = [w / sum(new_weights) for w in new_weights]
    new_score = calculate_new_score(result, new_weights)
    changes.append(((new_score - original_score) / original_score) * 100)
    
    # Reliability +10%
    new_weights = weights.copy()
    new_weights[2] *= 1.1
    new_weights = [w / sum(new_weights) for w in new_weights]
    new_score = calculate_new_score(result, new_weights)
    changes.append(((new_score - original_score) / original_score) * 100)
    
    # Reliability -10%
    new_weights = weights.copy()
    new_weights[2] *= 0.9
    new_weights = [w / sum(new_weights) for w in new_weights]
    new_score = calculate_new_score(result, new_weights)
    changes.append(((new_score - original_score) / original_score) * 100)
    
    return changes

def calculate_new_score(result: Dict[str, Any], weights: List[float]) -> float:
    """
    Calculate a new score with adjusted weights
    
    Args:
        result: Result dictionary for a forwarder
        weights: New weights
        
    Returns:
        New score
    """
    cost_score = (1 - result["costFactor"]) * weights[0]
    time_score = (1 - result["timeFactor"]) * weights[1]
    reliability_score = result["reliabilityFactor"] * weights[2]
    tracking_score = float(result["hasTracking"]) * weights[3]
    
    return cost_score + time_score + reliability_score + tracking_score


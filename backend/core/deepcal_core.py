"""
DeepCAL++ Core Engine
This module contains the core processing and TOPSIS ranking functionality
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Union, Tuple

def process_logistics_data(forwarders: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Process the input forwarder data into a format suitable for TOPSIS analysis
    
    Args:
        forwarders: List of dictionaries containing forwarder data
        
    Returns:
        Processed DataFrame ready for TOPSIS analysis
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

def run_topsis_analysis(
    data: pd.DataFrame, 
    weight_vector: List[float] = None,
    criteria_types: List[str] = None,
    analysis_depth: int = 3
) -> List[Dict[str, Any]]:
    """
    Run TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) analysis
    
    Args:
        data: DataFrame containing the processed forwarder data
        weight_vector: Optional custom weight vector for criteria
        criteria_types: List of 'benefit' or 'cost' for each criterion
        analysis_depth: Level of analysis detail (1-5)
        
    Returns:
        List of dictionaries containing ranked results
    """
    # Define default weights and criteria types if not provided
    if weight_vector is None:
        # Default weights: cost (40%), time (30%), reliability (20%), tracking (10%)
        weight_vector = [0.4, 0.3, 0.2, 0.1]
    
    if criteria_types is None:
        # Default criteria types: cost and time are 'cost' (lower is better)
        # reliability and tracking are 'benefit' (higher is better)
        criteria_types = ['cost', 'cost', 'benefit', 'benefit']
    
    # Extract relevant columns for analysis
    analysis_columns = ['cost', 'time', 'reliability']
    if 'tracking' in data.columns:
        analysis_columns.append('tracking')
    
    # Subset the data
    matrix = data[analysis_columns].values
    
    # Step 1: Normalize the decision matrix
    normalized_matrix = normalize_decision_matrix(matrix)
    
    # Step 2: Calculate weighted normalized decision matrix
    weights = np.array(weight_vector[:len(analysis_columns)])
    weighted_matrix = normalized_matrix * weights
    
    # Step 3: Determine ideal and negative-ideal solutions
    ideal_solution, negative_ideal = determine_ideal_solutions(
        weighted_matrix, 
        criteria_types[:len(analysis_columns)]
    )
    
    # Step 4: Calculate separation measures
    s_plus = calculate_separation(weighted_matrix, ideal_solution)
    s_minus = calculate_separation(weighted_matrix, negative_ideal)
    
    # Step 5: Calculate performance scores
    performance_scores = s_minus / (s_plus + s_minus)
    
    # Step 6: Create detailed results based on analysis depth
    results = []
    
    # Sort indices by performance score (descending)
    ranked_indices = np.argsort(performance_scores)[::-1]
    
    for rank, idx in enumerate(ranked_indices, 1):
        forwarder = data.iloc[idx]
        
        result = {
            "name": forwarder['name'],
            "rank": rank,
            "score": float(performance_scores[idx]),
        }
        
        # Add factor details based on analysis depth
        if analysis_depth >= 2:
            # Calculate normalized factor values (0-1 scale)
            result["cost_factor"] = normalized_matrix[idx, 0]
            result["time_factor"] = normalized_matrix[idx, 1]
            result["reliability_factor"] = normalized_matrix[idx, 2]
            
            if len(analysis_columns) > 3:
                result["tracking_factor"] = normalized_matrix[idx, 3]
        
        # Add raw values
        if analysis_depth >= 3:
            result["cost"] = float(forwarder['cost'])
            result["time"] = float(forwarder['time'])
            result["reliability"] = float(forwarder['reliability'])
            if 'tracking' in forwarder:
                result["tracking"] = bool(forwarder['tracking'])
        
        # Add separation measures and contributions
        if analysis_depth >= 4:
            result["separation_ideal"] = float(s_plus[idx])
            result["separation_negative"] = float(s_minus[idx])
            
            # Calculate individual criterion contributions
            criterion_contributions = calculate_criterion_contributions(
                weighted_matrix[idx], 
                ideal_solution,
                negative_ideal
            )
            result["criterion_contributions"] = criterion_contributions
        
        # Add sensitivity analysis
        if analysis_depth >= 5:
            result["sensitivity"] = perform_sensitivity_analysis(
                matrix, 
                weights,
                criteria_types[:len(analysis_columns)],
                idx
            )
        
        results.append(result)
    
    return results

def normalize_decision_matrix(matrix: np.ndarray) -> np.ndarray:
    """Normalize the decision matrix using vector normalization"""
    # Calculate column norms (Euclidean length of each column)
    norms = np.sqrt(np.sum(matrix**2, axis=0))
    
    # Avoid division by zero
    norms = np.where(norms == 0, 1e-10, norms)
    
    # Normalize each element
    normalized_matrix = matrix / norms
    
    return normalized_matrix

def determine_ideal_solutions(
    weighted_matrix: np.ndarray, 
    criteria_types: List[str]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Determine the ideal and negative-ideal solutions
    
    Args:
        weighted_matrix: The weighted normalized decision matrix
        criteria_types: List of 'benefit' or 'cost' for each criterion
        
    Returns:
        Tuple of ideal and negative-ideal solution vectors
    """
    ideal_solution = np.zeros(weighted_matrix.shape[1])
    negative_ideal = np.zeros(weighted_matrix.shape[1])
    
    for j in range(weighted_matrix.shape[1]):
        if criteria_types[j] == 'benefit':
            # For benefit criteria, higher values are better
            ideal_solution[j] = np.max(weighted_matrix[:, j])
            negative_ideal[j] = np.min(weighted_matrix[:, j])
        else:
            # For cost criteria, lower values are better
            ideal_solution[j] = np.min(weighted_matrix[:, j])
            negative_ideal[j] = np.max(weighted_matrix[:, j])
    
    return ideal_solution, negative_ideal

def calculate_separation(matrix: np.ndarray, reference_point: np.ndarray) -> np.ndarray:
    """
    Calculate the Euclidean distance between each alternative and a reference point
    
    Args:
        matrix: Decision matrix
        reference_point: Reference point (ideal or negative-ideal solution)
        
    Returns:
        Array of separation measures
    """
    return np.sqrt(np.sum((matrix - reference_point)**2, axis=1))

def calculate_criterion_contributions(
    alternative: np.ndarray,
    ideal: np.ndarray,
    negative_ideal: np.ndarray
) -> List[float]:
    """
    Calculate the contribution of each criterion to the performance score
    
    Args:
        alternative: Weighted normalized values for an alternative
        ideal: Ideal solution
        negative_ideal: Negative-ideal solution
        
    Returns:
        List of contribution percentages for each criterion
    """
    n_criteria = len(alternative)
    contributions = []
    
    for j in range(n_criteria):
        # Calculate distances for this criterion
        d_plus_j = (alternative[j] - ideal[j])**2
        d_minus_j = (alternative[j] - negative_ideal[j])**2
        
        # Calculate contribution
        if d_plus_j + d_minus_j > 0:
            contribution_j = d_minus_j / (d_plus_j + d_minus_j)
        else:
            contribution_j = 0
            
        contributions.append(float(contribution_j))
    
    return contributions

def perform_sensitivity_analysis(
    matrix: np.ndarray,
    weights: np.ndarray,
    criteria_types: List[str],
    alternative_idx: int
) -> Dict[str, List[float]]:
    """
    Perform simple sensitivity analysis by varying weights
    
    Args:
        matrix: Original decision matrix
        weights: Current weight vector
        criteria_types: List of 'benefit' or 'cost' for each criterion
        alternative_idx: Index of the alternative to analyze
        
    Returns:
        Dictionary with sensitivity analysis results
    """
    n_criteria = len(weights)
    sensitivity = {"weight_changes": [], "score_changes": []}
    
    # Calculate base score
    normalized_matrix = normalize_decision_matrix(matrix)
    weighted_matrix = normalized_matrix * weights
    
    ideal, negative_ideal = determine_ideal_solutions(weighted_matrix, criteria_types)
    s_plus = calculate_separation(weighted_matrix, ideal)
    s_minus = calculate_separation(weighted_matrix, negative_ideal)
    base_score = s_minus[alternative_idx] / (s_plus[alternative_idx] + s_minus[alternative_idx])
    
    # Test weight changes
    weight_changes = [-0.2, -0.1, 0.1, 0.2]  # Test 20% and 10% increases/decreases
    
    for i in range(n_criteria):
        for change in weight_changes:
            # Skip if change would make weight negative
            if weights[i] + change <= 0:
                continue
                
            # Create new weight vector
            new_weights = weights.copy()
            new_weights[i] += change
            
            # Normalize weights to sum to 1
            new_weights = new_weights / np.sum(new_weights)
            
            # Recalculate score
            weighted_matrix = normalized_matrix * new_weights
            ideal, negative_ideal = determine_ideal_solutions(weighted_matrix, criteria_types)
            s_plus = calculate_separation(weighted_matrix, ideal)
            s_minus = calculate_separation(weighted_matrix, negative_ideal)
            new_score = s_minus[alternative_idx] / (s_plus[alternative_idx] + s_minus[alternative_idx])
            
            # Calculate percentage change in score
            score_change = (new_score - base_score) / base_score * 100
            
            sensitivity["weight_changes"].append(f"Criterion {i+1}: {change:+.1f}")
            sensitivity["score_changes"].append(float(score_change))
    
    return sensitivity


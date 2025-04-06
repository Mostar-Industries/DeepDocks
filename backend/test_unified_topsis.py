#!/usr/bin/env python
"""
DeepCAL++ Unified TOPSIS Test Script
This script tests the unified TOPSIS implementation with different logic extensions
"""
import sys
import os
import numpy as np
import pandas as pd

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(parent_dir)

# Import the core engine
from backend.core.deepcal_core import run_topsis, process_logistics_data

def main():
    """
    Main function to test the unified TOPSIS implementation
    """
    print("Testing Unified TOPSIS Implementation")
    print("=====================================")
    
    # Create test data
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
        }
    ]
    
    # Process data
    df = process_logistics_data(forwarders)
    
    # Define weights and criteria types
    weights = [0.4, 0.3, 0.2, 0.1]  # cost, time, reliability, tracking
    criteria_types = ['cost', 'cost', 'benefit', 'benefit']
    
    # Run classic TOPSIS
    print("\nClassic TOPSIS Results:")
    classic_results = run_topsis(df, weights, criteria_types, use_neutrosophic=False, use_grey=False, analysis_depth=3)
    for result in classic_results:
        print(f"{result['rank']}. {result['name']} - Score: {result['score']:.3f}")
    
    # Run neutrosophic TOPSIS
    print("\nNeutrosophic TOPSIS Results:")
    neutrosophic_results = run_topsis(df, weights, criteria_types, use_neutrosophic=True, use_grey=False, analysis_depth=3)
    for result in neutrosophic_results:
        print(f"{result['rank']}. {result['name']} - Score: {result['score']:.3f}")
    
    # Run grey TOPSIS
    print("\nGrey TOPSIS Results:")
    grey_results = run_topsis(df, weights, criteria_types, use_neutrosophic=False, use_grey=True, analysis_depth=3)
    for result in grey_results:
        print(f"{result['rank']}. {result['name']} - Score: {result['score']:.3f}")
    
    print("\nTest completed successfully.")

if __name__ == "__main__":
    main()


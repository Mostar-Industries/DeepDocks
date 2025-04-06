#!/usr/bin/env python
"""
DeepCAL++ Integration Test Script
This script tests the integration between the API and the core engine
"""
import sys
import json
import os
from core.deepcal_core import run_neutrosophic_analysis
from core.deepcal_utils import build_pairwise_weights

def main():
    """
    Main function to test the integration
    """
    # Test data
    test_data = {
        "origin": "Kenya",
        "destination": "DR Congo",
        "weight": 200,
        "value": 12000,
        "urgency": "express",
        "criteria_pairwise": [
            [1, 0.5, 3, 2],
            [2, 1, 4, 2],
            [1/3, 1/4, 1, 0.5],
            [0.5, 0.5, 2, 1]
        ]
    }
    
    # Build weights from pairwise matrix
    weights = build_pairwise_weights(test_data["criteria_pairwise"])
    print(f"Weights: {weights}")
    
    # Generate mock forwarders
    forwarders = generate_mock_forwarders(test_data["origin"], test_data["destination"], test_data["weight"], test_data["value"])
    
    # Run neutrosophic analysis
    results = run_neutrosophic_analysis(forwarders, weights, urgency=test_data["urgency"])
    
    # Print results
    print(f"Top forwarder: {results[0]['name']}")
    print(f"Score: {results[0]['score']}")
    print(f"Rank: {results[0]['rank']}")
    
    # Print all results
    print("\nAll results:")
    for result in results:
        print(f"{result['rank']}. {result['name']} - Score: {result['score']:.3f}")
    
    # Save results to file for inspection
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nTest completed successfully. Results saved to test_results.json")

def generate_mock_forwarders(origin, destination, weight, value):
    """
    Generate mock forwarders for testing
    
    Args:
        origin: Origin location
        destination: Destination location
        weight: Shipment weight
        value: Shipment value
        
    Returns:
        List of forwarder dictionaries
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
    
    # Adjust costs based on weight and value
    weight_factor = weight / 1000
    value_factor = value / 10000 if value else 1
    
    for forwarder in forwarders:
        # Adjust cost based on weight and value
        forwarder["cost"] = forwarder["cost"] * (0.8 + weight_factor * 0.4) * (0.9 + value_factor * 0.2)
        
        # Round cost to nearest integer
        forwarder["cost"] = round(forwarder["cost"])
    
    return forwarders

if __name__ == "__main__":
    main()


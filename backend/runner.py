#!/usr/bin/env python
"""
DeepCAL++ Runner Script
This script serves as the entry point for the API to access the core engine
"""
import sys
import json
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

# Add parent directory to path to enable imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(parent_dir)

# Import core modules
from backend.core.deepcal_core import run_neutrosophic_analysis, load_forwarders_for_route
from backend.core.deepcal_utils import build_pairwise_weights
from backend.commentary.commentary import generate_commentary
from backend.data.data_mirror import get_data_mirror, mirror_data_from_supabase

def main():
    """
    Main function to process input from stdin and output results to stdout
    """
    try:
        # Read input from stdin
        raw_input = sys.stdin.read()
        request = json.loads(raw_input)
        
        # Extract request parameters
        origin = request.get("origin", "")
        destination = request.get("destination", "")
        weight = request.get("weight", 0)
        value = request.get("value", 0)
        urgency = request.get("urgency", "standard")
        cargo_type = request.get("cargoType", "general")
        
        # Extract criteria pairwise matrix or use default
        criteria_pairwise = request.get("criteria_pairwise", [
            [1, 0.5, 3, 2],
            [2, 1, 4, 2],
            [1/3, 1/4, 1, 1/2],
            [1/2, 1/2, 2, 1]
        ])

        # Extract criteria_types from the request
        criteria_types = request.get("criteria_types", ['cost', 'cost', 'benefit', 'benefit'])
        
        # Extract Supabase data if available
        supabase_data = request.get("supabase_data")
        
        # Mirror Supabase data to base data if available
        if supabase_data:
            mirror_data_from_supabase(supabase_data)
        
        # Build weights from pairwise matrix
        weights = build_pairwise_weights(criteria_pairwise)
        
        # Load forwarders for the given route
        forwarders = load_forwarders_for_route(
            origin, 
            destination, 
            cargo_type=cargo_type,
            use_supabase_data=True,
            supabase_data=supabase_data
        )
        
        # Run the neutrosophic analysis
        results = run_neutrosophic_analysis(
            forwarders, 
            weights, 
            urgency=urgency,
            criteria_types=criteria_types,
            supabase_data=supabase_data
        )
        
        # Generate commentary for the results
        commentary = generate_commentary(results, forwarders)
        
        # Prepare the response
        response = {
            "results": results,
            "weights": {
                "cost": weights[0],
                "time": weights[1],
                "reliability": weights[2],
                "tracking": weights[3]
            },
            "commentary": commentary,
            "analysisDepth": 5,
            "dataSource": "supabase" if supabase_data else "base_data"
        }
        
        # Output the response as JSON
        print(json.dumps(response))
        
    except Exception as e:
        # Handle errors
        error_response = {
            "error": str(e),
            "status": "error"
        }
        print(json.dumps(error_response))
        sys.exit(1)

if __name__ == "__main__":
    main()


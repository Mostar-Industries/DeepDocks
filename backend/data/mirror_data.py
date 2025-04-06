#!/usr/bin/env python
"""
DeepCAL++ Data Mirroring Script
This script mirrors data from Supabase to local base data
"""
import sys
import json
import os
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mirror_data")

# Add parent directory to path to enable imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(parent_dir)

# Import data mirror module
from backend.data.data_mirror import get_data_mirror

def main():
    """
    Main function to mirror data from Supabase to local base data
    """
    if len(sys.argv) < 2:
        logger.error("No input file specified")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        # Load data from input file
        with open(input_file, 'r') as f:
            supabase_data = json.load(f)
        
        # Get data mirror instance
        data_mirror = get_data_mirror()
        
        # Mirror data
        success = data_mirror.mirror_supabase_data(supabase_data)
        
        if success:
            logger.info("Data mirrored successfully")
            sys.exit(0)
        else:
            logger.error("Failed to mirror data")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error mirroring data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


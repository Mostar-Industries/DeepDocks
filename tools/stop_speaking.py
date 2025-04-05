#!/usr/bin/env python
"""
DeepCAL++ Stop Speaking Script
This script stops any ongoing speech
"""
import os
import sys

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(parent_dir)

# Import voice module
from backend.voice.speak import stop_speaking

def main():
    """Main function"""
    # Stop speaking
    success = stop_speaking()
    
    if not success:
        print("Error: Failed to stop speaking")
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()


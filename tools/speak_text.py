#!/usr/bin/env python
"""
DeepCAL++ Speak Text Script
This script speaks text using the DeepCAL++ voice system
"""
import os
import sys
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("speak_text")

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(parent_dir)

# Import voice module
from backend.voice.speak import speak_text, get_voice_usage_stats

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Speak text using DeepCAL++ voice system")
    parser.add_argument("text", help="Text to speak")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech rate multiplier")
    parser.add_argument("--stats", action="store_true", help="Show voice usage statistics")
    
    args = parser.parse_args()
    
    # Show usage stats if requested
    if args.stats:
        stats = get_voice_usage_stats()
        print("Voice Usage Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        sys.exit(0)
    
    # Speak the text
    logger.info(f"Speaking at speed {args.speed}")
    success = speak_text(args.text, blocking=True, speed=args.speed)
    
    if not success:
        logger.error("Error: Failed to speak text")
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()


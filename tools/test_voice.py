#!/usr/bin/env python
"""
DeepCAL++ Voice Test Script
This script tests the voice functionality
"""
import os
import sys
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_voice")

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(parent_dir)

# Import voice module
from backend.voice.speak import speak_text, get_voice_usage_stats

def main():
  """Main function"""
  parser = argparse.ArgumentParser(description="Test DeepCAL++ voice system")
  parser.add_argument("--text", default="Hello, this is a test of the DeepCAL++ voice service.", 
                      help="Text to speak")
  parser.add_argument("--stats", action="store_true", help="Show usage statistics")
  
  args = parser.parse_args()
  
  # Show usage stats if requested
  if args.stats:
      stats = get_voice_usage_stats()
      print("Voice Usage Statistics:")
      for key, value in stats.items():
          print(f"  {key}: {value}")
      sys.exit(0)
  
  # Speak the text
  logger.info(f"Speaking: {args.text}")
  success = speak_text(args.text, blocking=True)
  
  if not success:
      logger.error("Error: Failed to speak text")
      sys.exit(1)
  
  logger.info("Voice test completed successfully")
  sys.exit(0)

if __name__ == "__main__":
  main()


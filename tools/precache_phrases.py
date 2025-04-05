#!/usr/bin/env python
"""
DeepCAL++ Phrase Pre-caching Tool
This script pre-caches common phrases to minimize ElevenLabs API calls
"""
import os
import sys
import argparse
import logging
import json
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("precache_phrases")

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(parent_dir)

# Import voice module
from backend.voice.speak import speak_text

def load_phrases(file_path: str = None) -> List[str]:
    """
    Load phrases from a file or use default phrases
    
    Args:
        file_path: Path to JSON file with phrases
        
    Returns:
        List of phrases to pre-cache
    """
    default_phrases = [
        # Welcome and introduction phrases
        "Hello there! I'm DeepCAL++. How can I assist you today?",
        "Welcome to DeepCAL++. I'm your logistics intelligence assistant.",
        "It's a pleasure to meet you! I'm DeepCAL++, your logistics intelligence assistant.",
        "How can I help optimize your logistics operations today?",
        
        # Analysis phrases
        "I've analyzed the logistics data for your shipment.",
        "Based on my analysis, I recommend the following route.",
        "I've calculated the optimal logistics route for your shipment with 95% confidence.",
        "Based on historical data, the most reliable carrier for this route is ExpressShip.",
        "Your shipment from Kenya to DR Congo should take approximately 14 days via air freight.",
        "I've analyzed 7 potential carriers and ranked them based on cost, time, and reliability.",
        "The TOPSIS analysis indicates AfricaLogistics offers the best balance of factors for your needs.",
        "I've found three potential routes for your shipment, with varying cost-time tradeoffs.",
        "My analysis shows a 23% cost saving opportunity if you're flexible with delivery time.",
        
        # Alert phrases
        "Alert: Data completeness below threshold for Nigeria-Ghana route.",
        "Alert: I've detected an anomaly in the logistics data.",
        "Alert: Potential delay detected in Nigeria-Ghana route.",
        "Alert: Weather conditions may affect delivery times in East Africa.",
        "Alert: Critical delay detected in Kenya-DRC route.",
        "Alert: System unable to connect to logistics provider API.",
        
        # Conversation phrases
        "Would you like me to provide more details?",
        "Is there anything else you'd like to know?",
        "Thank you for using DeepCAL++. Have a great day!",
        "I'm processing your request. This will take a moment.",
        "The optimal route has been calculated.",
        "Please provide more information about your shipment.",
        
        # Humor phrases
        "I calculated that faster than a caffeinated logistics manager on a Monday!",
        "If logistics were a sport, this would definitely be a gold medal solution.",
        "I'd bet my last processing cycle that this is the optimal route.",
        "My circuits are practically glowing with pride at this recommendation.",
        "This analysis is so precise, even my debugging module is impressed.",
        "I've analyzed more routes than there are stars in the Milky Way... well, almost.",
        "This solution is so elegant, it deserves its own logistics award.",
        "If I had a physical form, I'd be giving you a thumbs up right now.",
        "My quantum logistics algorithm is practically doing a victory dance.",
        "This recommendation is fresher than newly written code!"
    ]
    
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                phrases = json.load(f)
            
            if isinstance(phrases, list) and all(isinstance(p, str) for p in phrases):
                logger.info(f"Loaded {len(phrases)} phrases from {file_path}")
                return phrases
            else:
                logger.warning(f"Invalid format in {file_path}. Using default phrases.")
        except Exception as e:
            logger.error(f"Error loading phrases from {file_path}: {e}")
    
    logger.info(f"Using {len(default_phrases)} default phrases")
    return default_phrases

def main():
  """Main function"""
  parser = argparse.ArgumentParser(description="Pre-cache common phrases for DeepCAL++ voice system")
  parser.add_argument("--file", help="Path to JSON file with phrases to pre-cache")
  
  args = parser.parse_args()
  
  # Load phrases
  phrases = load_phrases(args.file)
  
  # Pre-cache phrases
  logger.info(f"Pre-caching {len(phrases)} phrases...")
  
  for phrase in phrases:
      logger.info(f"Pre-caching: {phrase[:30]}...")
      speak_text(phrase, blocking=True)
  
  logger.info(f"Pre-caching complete: {len(phrases)} phrases processed")
  
  sys.exit(0)

if __name__ == "__main__":
    main()


#!/usr/bin/env python
"""
DeepCAL++ Anomaly Simulator
This script simulates anomalies for testing the alert system
"""
import os
import sys
import argparse
import json
import time

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(parent_dir)

# Import voice module
from backend.voice.speak import speak_text

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Simulate anomalies for DeepCAL++")
    parser.add_argument("--level", choices=["info", "warning", "critical"], default="warning", 
                        help="Anomaly level")
    parser.add_argument("--message", default="", help="Custom anomaly message")
    
    args = parser.parse_args()
    
    # Default messages by level
    default_messages = {
        "info": "System performance metrics updated",
        "warning": "Data completeness below threshold for South Africa shipments",
        "critical": "Critical delay detected in Kenya-DRC route"
    }
    
    # Use custom message or default
    message = args.message if args.message else default_messages[args.level]
    
    # Create anomaly data
    anomaly = {
        "id": f"anomaly-{int(time.time())}",
        "message": message,
        "level": args.level,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source": "DeepCAL++ Anomaly Simulator"
    }
    
    # Print anomaly data
    print(json.dumps(anomaly, indent=2))
    
    # Speak the alert
    if args.level == "critical":
        alert_text = f"Critical Alert: {message}"
    elif args.level == "warning":
        alert_text = f"Warning: {message}"
    else:
        alert_text = f"Information: {message}"
    
    speak_text(alert_text, blocking=True, voice_type="custom")
    
    sys.exit(0)

if __name__ == "__main__":
    main()


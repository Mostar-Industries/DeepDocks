#!/usr/bin/env python
"""
DeepCAL++ Cron Health Check
This script is designed to be run via cron to perform scheduled health checks
and log the results to Supabase.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
import requests
from typing import Dict, Any

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(parent_dir)

# Import health check module
from backend.cli.check_status import HealthCheck

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(parent_dir, "backend", "logs", "cron_health_check.log"),
    filemode='a'
)
logger = logging.getLogger("cron_health_check")

# Environment variables
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SYSTEM_ID = os.getenv("SYSTEM_ID", "primary")
LOG_TO_SUPABASE = os.getenv("LOG_TO_SUPABASE", "true").lower() in ["true", "1", "yes", "y"]
ALERT_ON_ERROR = os.getenv("ALERT_ON_ERROR", "true").lower() in ["true", "1", "yes", "y"]
ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "")

def log_to_supabase(results: Dict[str, Any]) -> bool:
    """
    Log health check results to Supabase
    
    Args:
        results: Health check results
        
    Returns:
        True if successful, False otherwise
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        logger.error("Supabase URL or service key not set")
        return False
    
    try:
        # Prepare data for Supabase
        data = {
            "timestamp": results["timestamp"],
            "system_id": SYSTEM_ID,
            "overall_status": results["overall_status"],
            "execution_time_ms": results["execution_time_ms"],
            "details": results
        }
        
        # Send data to Supabase
        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/system_health_logs",
            headers=headers,
            json=data
        )
        
        if response.status_code in [201, 200]:
            logger.info("Health check results logged to Supabase successfully")
            return True
        else:
            logger.error(f"Failed to log health check results to Supabase: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error logging health check results to Supabase: {str(e)}")
        return False

def send_alert(results: Dict[str, Any]) -> bool:
    """
    Send alert for non-ok health check results
    
    Args:
        results: Health check results
        
    Returns:
        True if successful, False otherwise
    """
    if not ALERT_WEBHOOK_URL:
        logger.warning("Alert webhook URL not set")
        return False
    
    try:
        # Prepare alert data
        alert_data = {
            "timestamp": results["timestamp"],
            "system_id": SYSTEM_ID,
            "status": results["overall_status"],
            "message": f"DeepCAL++ Health Check Alert: {results['overall_status'].upper()}",
            "details": {}
        }
        
        # Add details for non-ok components
        for component_name, component in results.items():
            if isinstance(component, dict) and "status" in component and component["status"] not in ["ok", "skipped"]:
                alert_data["details"][component_name] = {
                    "status": component["status"],
                    "message": component["message"]
                }
        
        # Send alert
        response = requests.post(
            ALERT_WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            json=alert_data
        )
        
        if response.status_code in [200, 201, 202, 204]:
            logger.info("Alert sent successfully")
            return True
        else:
            logger.error(f"Failed to send alert: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error sending alert: {str(e)}")
        return False

def main():
    """Main function for cron usage"""
    logger.info("Starting scheduled health check")
    
    try:
        # Run health check
        health_check = HealthCheck(check_voice=False)
        results = health_check.run_all_checks()
        
        # Log results to file
        log_file = os.path.join(parent_dir, "backend", "logs", "health_check_history.json")
        
        try:
            # Load existing history
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    history = json.load(f)
            else:
                history = {"checks": []}
            
            # Add new results
            history["checks"].append({
                "timestamp": results["timestamp"],
                "status": results["overall_status"],
                "execution_time_ms": results["execution_time_ms"]
            })
            
            # Keep only the last 100 checks
            if len(history["checks"]) > 100:
                history["checks"] = history["checks"][-100:]
            
            # Save updated history
            with open(log_file, "w") as f:
                json.dump(history, f, indent=2)
            
            logger.info("Health check results logged to file")
        
        except Exception as e:
            logger.error(f"Error logging health check results to file: {str(e)}")
        
        # Log to Supabase if enabled
        if LOG_TO_SUPABASE:
            log_to_supabase(results)
        
        # Send alert if needed
        if ALERT_ON_ERROR and results["overall_status"] != "ok":
            send_alert(results)
        
        logger.info(f"Scheduled health check completed with status: {results['overall_status']}")
        
        # Return exit code based on status
        return 0 if results["overall_status"] == "ok" else 1
    
    except Exception as e:
        logger.error(f"Error running scheduled health check: {str(e)}")
        
        # Try to send alert for the exception
        if ALERT_ON_ERROR and ALERT_WEBHOOK_URL:
            try:
                alert_data = {
                    "timestamp": datetime.now().isoformat(),
                    "system_id": SYSTEM_ID,
                    "status": "error",
                    "message": f"DeepCAL++ Health Check Exception: {str(e)}",
                    "details": {
                        "exception": str(e)
                    }
                }
                
                requests.post(
                    ALERT_WEBHOOK_URL,
                    headers={"Content-Type": "application/json"},
                    json=alert_data
                )
            except:
                pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())


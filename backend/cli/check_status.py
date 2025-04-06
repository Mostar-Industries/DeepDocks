#!/usr/bin/env python
"""
DeepCAL++ System Health Checker
Checks Supabase connection, base data availability,
API endpoint status, and core engine version with personality.
"""

import os
import sys
import time
import json
import random
import requests
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(parent_dir)

# Import required modules
try:
    from backend.data.data_mirror import get_data_mirror
    from backend.core.deepcal_core import run_neutrosophic_analysis
    from backend.voice.speak import check_voice_availability, speak_text
except ImportError:
    # Handle case when running standalone
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("health_check")

# Environment variables
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
DEEPCAL_API_URL = os.getenv("DEEPCAL_API_URL", "http://localhost:3000/api/rank")
DEEPCAL_API_KEY = os.getenv("DEEPCAL_API_KEY", "")
BASE_DATA_DIR = os.getenv("DATA_DIRECTORY", "backend/data/base_data")
TRAINING_DATA_DIR = os.getenv("TRAINING_DATA_DIRECTORY", "backend/data/training_data")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "backend/logs/system.log")

# ANSI color codes
COLORS = {
    "reset": "\033[0m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "bold": "\033[1m"
}

# Personality phrases
PERSONALITY_PHRASES = {
    "intro": [
        "Initiating system diagnostics. Let's see what we're working with today...",
        "Running health check. This is where I get to judge my own code. Fun!",
        "System check time! Let's see if everything's running as brilliantly as I designed it.",
        "Diagnostic sequence initiated. Prepare for the cold, hard truth about our system.",
        "Health check in progress. I'll be the judge of how healthy we really are."
    ],
    "all_good": [
        "All systems operational! I'm calculating optimal routes faster than a caffeinated logistics manager on Monday morning!",
        "Everything's running smoothly! My quantum logistics algorithm is practically doing a victory dance.",
        "Systems check complete: We're green across the board! I'd bet my last processing cycle this is the most optimized logistics system in Africa.",
        "All clear! My circuits are practically glowing with pride at how well everything's running.",
        "System health is optimal! This solution is so elegant, it deserves its own logistics award."
    ],
    "minor_issues": [
        "Minor issues detected. Nothing I can't handle, but let's not ignore them like DHL ignores delivery windows.",
        "A few hiccups in the system. Not critical, but they're annoying me like misrouted packages.",
        "Some non-critical warnings to report. They're like potholes on a Nigerian highway - annoying but navigable.",
        "I've found a few issues that need attention. Nothing urgent, but they're slowing me down like Kenyan customs paperwork.",
        "Minor problems detected. They're like small delays in the supply chain - not catastrophic, but still irritating."
    ],
    "major_issues": [
        "Critical issues detected! My logistics calculations are about as reliable as a paper boat in a thunderstorm right now.",
        "ALERT: Major system problems! I'm about as functional as a delivery truck with four flat tires.",
        "Critical failure! My optimization engine is struggling more than a freight forwarder during port strikes.",
        "Major system issues detected! I'm operating at the efficiency of a 1970s cargo ship with engine problems.",
        "SOS: Critical system failures! My neural networks are more tangled than West African customs regulations."
    ],
    "supabase_good": [
        "Supabase connection is solid! Data flowing smoother than express shipments through Moroccan customs.",
        "Database connection: Optimal! Retrieving data faster than ExpressShip's premium service.",
        "Supabase link is strong! Data transmission clearer than AfricaLogistics' tracking updates."
    ],
    "supabase_bad": [
        "Supabase connection failed! I'm as cut off from data as a shipment lost in the Sahara.",
        "Database unreachable! I feel like a logistics manager whose internet just went down during peak season.",
        "Can't connect to Supabase! I'm flying blind like a cargo plane with no navigation system."
    ],
    "api_good": [
        "API endpoints responding perfectly! Faster than GlobalFreight's customer service (which isn't saying much).",
        "API check: All green! Endpoints more reliable than TransAfrica's premium service.",
        "API is rock solid! Responses coming in faster than FastCargo lives up to its name."
    ],
    "api_bad": [
        "API endpoints down! I'm about as useful as a logistics app without internet right now.",
        "API failure detected! I'm struggling to communicate like a freight ship with a broken radio.",
        "API endpoints unresponsive! I feel like a tracking system during a network outage."
    ],
    "data_good": [
        "Base data integrity confirmed! My knowledge base is more complete than AfricaLogistics' route network.",
        "Data files all present and correct! I'm fully loaded like a cargo ship ready to sail.",
        "Data check passed! My datasets are more organized than ExpressShip's warehouse system."
    ],
    "data_bad": [
        "Data files missing! I'm working with less information than a customs officer on their first day.",
        "Critical data not found! I feel like a GPS with half the map missing.",
        "Data integrity compromised! My datasets are more incomplete than GlobalFreight's delivery records."
    ],
    "recommendation": [
        "Recommendation: Run 'deepcal refresh training' to incorporate the latest logistics patterns.",
        "Suggestion: Update base data files to improve prediction accuracy for East African routes.",
        "Action needed: Sync with Supabase to ensure we have the latest forwarder performance metrics.",
        "Consider running 'deepcal test-api' to verify endpoint performance under load.",
        "You might want to check the logs for more details on those minor hiccups I mentioned."
    ]
}

class HealthCheck:
    """
    System health check functionality for DeepCAL++
    """
    def __init__(self, check_supabase: bool = True, check_voice: bool = True, 
                 test_mode: bool = False, test_scenario: str = None):
        """
        Initialize health check
        
        Args:
            check_supabase: Whether to check Supabase connectivity
            check_voice: Whether to check voice system
            test_mode: Whether to run in test mode (simulate failures)
            test_scenario: Specific test scenario to simulate
        """
        self.check_supabase = check_supabase
        self.check_voice = check_voice
        self.test_mode = test_mode
        self.test_scenario = test_scenario
        
        try:
            self.data_mirror = get_data_mirror()
        except:
            self.data_mirror = None
        
        # Load environment variables
        self.supabase_url = SUPABASE_URL
        self.supabase_key = SUPABASE_ANON_KEY
        self.service_key = SUPABASE_SERVICE_KEY
        self.api_key = DEEPCAL_API_KEY
        self.api_url = DEEPCAL_API_URL
        
    def check_environment(self) -> Dict[str, Any]:
        """
        Check environment variables
        
        Returns:
            Dictionary with environment check results
        """
        required_vars = ["DEEPCAL_API_KEY", "NEXT_PUBLIC_SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_ANON_KEY"]
        optional_vars = ["SUPABASE_SERVICE_KEY", "VOICE_ENABLED", "DATA_DIRECTORY", "LOG_LEVEL"]
        
        env_status = {
            "status": "ok",
            "required": {},
            "optional": {},
            "message": "All required environment variables are set"
        }
        
        # Check required variables
        missing = []
        for var in required_vars:
            value = os.getenv(var)
            env_status["required"][var] = bool(value)
            if not value:
                missing.append(var)
        
        # Check optional variables
        for var in optional_vars:
            env_status["optional"][var] = bool(os.getenv(var))
        
        # Update status if any required variables are missing
        if missing:
            env_status["status"] = "error"
            env_status["message"] = f"Missing required environment variables: {', '.join(missing)}"
        
        # Simulate environment issues in test mode
        if self.test_mode and self.test_scenario == "env_missing":
            env_status["status"] = "error"
            env_status["message"] = "TEST MODE: Simulating missing environment variables"
            env_status["required"]["DEEPCAL_API_KEY"] = False
            missing.append("DEEPCAL_API_KEY")
        
        return env_status
    
    def check_data_files(self) -> Dict[str, Any]:
        """
        Check data files
        
        Returns:
            Dictionary with data files check results
        """
        data_status = {
            "status": "ok",
            "base_data": {},
            "training_data": {},
            "message": "All data files are accessible"
        }
        
        # Check base data directory
        base_data_dir = os.path.join(parent_dir, BASE_DATA_DIR)
        if not os.path.exists(base_data_dir):
            data_status["status"] = "warning"
            data_status["message"] = f"Base data directory not found: {base_data_dir}"
            return data_status
        
        # Check base data files
        base_files = ["forwarders.json", "routes.json", "rate_cards.json", "shipments.json"]
        for file in base_files:
            file_path = os.path.join(base_data_dir, file)
            exists = os.path.exists(file_path)
            
            # Simulate file corruption in test mode
            if self.test_mode and self.test_scenario == "data_corrupt" and file == "forwarders.json":
                exists = False
            
            data_status["base_data"][file] = {
                "exists": exists,
                "size_kb": round(os.path.getsize(file_path) / 1024, 2) if exists else 0,
                "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat() if exists else None
            }
        
        # Check training data directory
        training_data_dir = os.path.join(parent_dir, TRAINING_DATA_DIR)
        if not os.path.exists(training_data_dir):
            data_status["status"] = "warning"
            data_status["message"] = f"Training data directory not found: {training_data_dir}"
            return data_status
        
        # Check training data files
        training_files = ["topsis_training.json"]
        for file in training_files:
            file_path = os.path.join(training_data_dir, file)
            exists = os.path.exists(file_path)
            data_status["training_data"][file] = {
                "exists": exists,
                "size_kb": round(os.path.getsize(file_path) / 1024, 2) if exists else 0,
                "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat() if exists else None
            }
        
        # Check if any files are missing
        missing_base = [file for file, info in data_status["base_data"].items() if not info["exists"]]
        missing_training = [file for file, info in data_status["training_data"].items() if not info["exists"]]
        
        if missing_base or missing_training:
            data_status["status"] = "warning"
            data_status["message"] = "Some data files are missing"
            data_status["missing_files"] = {
                "base_data": missing_base,
                "training_data": missing_training
            }
        
        return data_status
    
    def check_supabase_connection(self) -> Dict[str, Any]:
        """
        Check Supabase connection
        
        Returns:
            Dictionary with Supabase connection check results
        """
        if not self.check_supabase:
            return {"status": "skipped", "message": "Supabase check skipped"}
        
        supabase_status = {
            "status": "ok",
            "message": "Supabase connection successful",
            "tables": {}
        }
        
        if not self.supabase_url or not self.supabase_key:
            supabase_status["status"] = "error"
            supabase_status["message"] = "Supabase URL or key not set"
            return supabase_status
        
        # Simulate Supabase connection failure in test mode
        if self.test_mode and self.test_scenario == "supabase_down":
            supabase_status["status"] = "error"
            supabase_status["message"] = "TEST MODE: Simulating Supabase connection failure"
            supabase_status["latency_ms"] = 0
            return supabase_status
        
        # Check Supabase connection
        try:
            # Simple health check request to Supabase
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}"
            }
            
            # Measure latency
            start_time = time.time()
            
            # Check forwarders table
            response = requests.get(
                f"{self.supabase_url}/rest/v1/forwarders?select=count",
                headers=headers
            )
            
            # Calculate latency
            latency_ms = round((time.time() - start_time) * 1000, 2)
            supabase_status["latency_ms"] = latency_ms
            
            if response.status_code != 200:
                supabase_status["status"] = "error"
                supabase_status["message"] = f"Failed to connect to Supabase: {response.status_code}"
                return supabase_status
            
            # Check other tables
            tables = ["forwarders", "routes", "rate_cards", "shipments"]
            for table in tables:
                try:
                    response = requests.get(
                        f"{self.supabase_url}/rest/v1/{table}?select=count",
                        headers=headers
                    )
                    
                    supabase_status["tables"][table] = {
                        "accessible": response.status_code == 200,
                        "status_code": response.status_code
                    }
                    
                    if response.status_code == 200:
                        # Try to get count
                        try:
                            count_response = requests.get(
                                f"{self.supabase_url}/rest/v1/{table}?select=count",
                                headers={**headers, "Prefer": "count=exact"}
                            )
                            count = int(count_response.headers.get("content-range", "0").split("/")[1])
                            supabase_status["tables"][table]["count"] = count
                        except Exception:
                            supabase_status["tables"][table]["count"] = "unknown"
                except Exception as e:
                    supabase_status["tables"][table] = {
                        "accessible": False,
                        "error": str(e)
                    }
            
            # Check if any tables are inaccessible
            inaccessible = [table for table, info in supabase_status["tables"].items() 
                           if not info.get("accessible", False)]
            
            if inaccessible:
                supabase_status["status"] = "warning"
                supabase_status["message"] = f"Some tables are inaccessible: {', '.join(inaccessible)}"
            
        except Exception as e:
            supabase_status["status"] = "error"
            supabase_status["message"] = f"Failed to connect to Supabase: {str(e)}"
        
        return supabase_status
    
    def check_api_endpoints(self) -> Dict[str, Any]:
        """
        Check API endpoints
        
        Returns:
            Dictionary with API endpoints check results
        """
        api_status = {
            "status": "ok",
            "endpoints": {},
            "message": "All API endpoints are accessible"
        }
        
        # Simulate API endpoint failure in test mode
        if self.test_mode and self.test_scenario == "api_down":
            api_status["status"] = "error"
            api_status["message"] = "TEST MODE: Simulating API endpoint failure"
            api_status["endpoints"]["rank"] = {
                "accessible": False,
                "status_code": 500,
                "latency_ms": 0,
                "error": "TEST MODE: Simulated API failure"
            }
            return api_status
        
        # Check rank endpoint
        try:
            # Prepare test data
            test_data = {
                "origin": "Kenya",
                "destination": "DR Congo",
                "weight": 200,
                "value": 12000,
                "urgency": "express",
                "cargoType": "general",
                "fragile": False,
                "hazardous": False,
                "perishable": False
            }
            
            # Measure latency
            start_time = time.time()
            
            # Make request
            response = requests.post(
                self.api_url,
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Calculate latency
            latency_ms = round((time.time() - start_time) * 1000, 2)
            
            api_status["endpoints"]["rank"] = {
                "accessible": response.status_code == 200,
                "status_code": response.status_code,
                "latency_ms": latency_ms
            }
            
            if response.status_code != 200:
                api_status["status"] = "error"
                api_status["message"] = f"API endpoint /api/rank returned status code {response.status_code}"
                api_status["endpoints"]["rank"]["error"] = response.text
            else:
                # Check response structure
                result = response.json()
                if "results" not in result or not isinstance(result["results"], list):
                    api_status["status"] = "warning"
                    api_status["message"] = "API endpoint /api/rank returned invalid response structure"
                    api_status["endpoints"]["rank"]["warning"] = "Invalid response structure"
                else:
                    api_status["endpoints"]["rank"]["forwarders_count"] = len(result["results"])
        
        except Exception as e:
            api_status["status"] = "error"
            api_status["message"] = f"Failed to connect to API endpoint /api/rank: {str(e)}"
            api_status["endpoints"]["rank"] = {
                "accessible": False,
                "error": str(e)
            }
        
        return api_status
    
    def check_core_engine(self) -> Dict[str, Any]:
        """
        Check core engine functionality
        
        Returns:
            Dictionary with core engine check results
        """
        engine_status = {
            "status": "ok",
            "message": "Core engine is functioning properly",
            "tests": {}
        }
        
        # Simulate core engine failure in test mode
        if self.test_mode and self.test_scenario == "engine_failure":
            engine_status["status"] = "error"
            engine_status["message"] = "TEST MODE: Simulating core engine failure"
            engine_status["tests"]["data_loading"] = {
                "success": False,
                "error": "TEST MODE: Simulated engine failure"
            }
            return engine_status
        
        # Test data loading
        try:
            # Import here to avoid circular imports
            from backend.core.deepcal_core import load_forwarders_for_route
            
            start_time = time.time()
            forwarders = load_forwarders_for_route("Kenya", "DR Congo", "general")
            load_time = time.time() - start_time
            
            engine_status["tests"]["data_loading"] = {
                "success": len(forwarders) > 0,
                "forwarders_count": len(forwarders),
                "load_time_ms": round(load_time * 1000, 2)
            }
            
            if len(forwarders) == 0:
                engine_status["status"] = "warning"
                engine_status["message"] = "No forwarders found for test route"
        except Exception as e:
            engine_status["status"] = "error"
            engine_status["message"] = f"Failed to load forwarders: {str(e)}"
            engine_status["tests"]["data_loading"] = {
                "success": False,
                "error": str(e)
            }
            return engine_status
        
        # Test data mirroring
        try:
            if self.data_mirror:
                mirror_cache = self.data_mirror._load_mirror_cache()
                engine_status["tests"]["data_mirror"] = {
                    "success": True,
                    "cache_size": {
                        "forwarders": len(mirror_cache.get("forwarders", [])),
                        "routes": len(mirror_cache.get("routes", [])),
                        "rate_cards": len(mirror_cache.get("rate_cards", [])),
                        "shipments": len(mirror_cache.get("shipments", []))
                    },
                    "last_sync": self.data_mirror._load_last_sync_time()
                }
                
                # Check if mirror cache is empty
                if all(len(mirror_cache.get(key, [])) == 0 for key in ["forwarders", "routes", "rate_cards", "shipments"]):
                    engine_status["status"] = "warning"
                    engine_status["message"] = "Data mirror cache is empty"
        except Exception as e:
            engine_status["tests"]["data_mirror"] = {
                "success": False,
                "error": str(e)
            }
        
        return engine_status
    
    def check_voice_system(self) -> Dict[str, Any]:
        """
        Check voice system
        
        Returns:
            Dictionary with voice system check results
        """
        if not self.check_voice:
            return {"status": "skipped", "message": "Voice system check skipped"}
        
        voice_status = {
            "status": "ok",
            "message": "Voice system is functioning properly",
            "available": False
        }
        
        # Simulate voice system failure in test mode
        if self.test_mode and self.test_scenario == "voice_unavailable":
            voice_status["status"] = "warning"
            voice_status["message"] = "TEST MODE: Simulating voice system unavailability"
            voice_status["available"] = False
            return voice_status
        
        try:
            voice_available = check_voice_availability()
            voice_status["available"] = voice_available
            
            if not voice_available:
                voice_status["status"] = "warning"
                voice_status["message"] = "Voice system is not available"
        except Exception as e:
            voice_status["status"] = "error"
            voice_status["message"] = f"Failed to check voice system: {str(e)}"
        
        return voice_status
    
    def check_logs(self) -> Dict[str, Any]:
        """
        Check log files
        
        Returns:
            Dictionary with log files check results
        """
        logs_status = {
            "status": "ok",
            "message": "Log files are accessible",
            "log_file": {}
        }
        
        # Check if log directory exists
        log_dir = os.path.dirname(LOG_FILE_PATH)
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
                logs_status["message"] = f"Created log directory: {log_dir}"
            except Exception as e:
                logs_status["status"] = "warning"
                logs_status["message"] = f"Failed to create log directory: {str(e)}"
                return logs_status
        
        # Check if log file exists
        if os.path.exists(LOG_FILE_PATH):
            logs_status["log_file"] = {
                "exists": True,
                "size_kb": round(os.path.getsize(LOG_FILE_PATH) / 1024, 2),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(LOG_FILE_PATH)).isoformat()
            }
            
            # Check if log file is writable
            try:
                with open(LOG_FILE_PATH, "a") as f:
                    pass
                logs_status["log_file"]["writable"] = True
            except Exception:
                logs_status["log_file"]["writable"] = False
                logs_status["status"] = "warning"
                logs_status["message"] = "Log file is not writable"
        else:
            logs_status["log_file"] = {
                "exists": False
            }
            
            # Try to create log file
            try:
                with open(LOG_FILE_PATH, "w") as f:
                    f.write(f"Log file created at {datetime.now().isoformat()}\n")
                logs_status["log_file"]["exists"] = True
                logs_status["log_file"]["writable"] = True
                logs_status["log_file"]["size_kb"] = 0
                logs_status["log_file"]["last_modified"] = datetime.now().isoformat()
                logs_status["message"] = "Created new log file"
            except Exception as e:
                logs_status["status"] = "warning"
                logs_status["message"] = f"Failed to create log file: {str(e)}"
        
        return logs_status
    
    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all health checks
        
        Returns:
            Dictionary with all health check results
        """
        start_time = time.time()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "environment": self.check_environment(),
            "data_files": self.check_data_files(),
            "core_engine": self.check_core_engine(),
            "logs": self.check_logs(),
            "overall_status": "ok",
            "test_mode": self.test_mode
        }
        
        # Add Supabase check if enabled
        if self.check_supabase:
            results["supabase"] = self.check_supabase_connection()
        
        # Add API endpoints check
        results["api"] = self.check_api_endpoints()
        
        # Add voice check if enabled
        if self.check_voice:
            results["voice"] = self.check_voice_system()
        
        # Calculate execution time
        results["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
        
        # Determine overall status
        status_priority = {"error": 0, "warning": 1, "ok": 2, "skipped": 3}
        statuses = [component["status"] for component in results.values() 
                   if isinstance(component, dict) and "status" in component]
        
        if statuses:
            # Get the highest priority status (lowest value)
            results["overall_status"] = min(statuses, key=lambda s: status_priority.get(s, 4))
        
        # Add personality
        results["personality"] = self.generate_personality_message(results)
        
        return results
    
    def generate_personality_message(self, results: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate personality-driven messages based on health check results
        
        Args:
            results: Health check results
            
        Returns:
            Dictionary with personality messages
        """
        personality = {
            "intro": random.choice(PERSONALITY_PHRASES["intro"]),
            "conclusion": "",
            "details": []
        }
        
        # Generate conclusion based on overall status
        if results["overall_status"] == "ok":
            personality["conclusion"] = random.choice(PERSONALITY_PHRASES["all_good"])
        elif results["overall_status"] == "warning":
            personality["conclusion"] = random.choice(PERSONALITY_PHRASES["minor_issues"])
        else:
            personality["conclusion"] = random.choice(PERSONALITY_PHRASES["major_issues"])
        
        # Add component-specific messages
        if "supabase" in results:
            if results["supabase"]["status"] == "ok":
                personality["details"].append(random.choice(PERSONALITY_PHRASES["supabase_good"]))
            elif results["supabase"]["status"] in ["error", "warning"]:
                personality["details"].append(random.choice(PERSONALITY_PHRASES["supabase_bad"]))
        
        if "api" in results:
            if results["api"]["status"] == "ok":
                personality["details"].append(random.choice(PERSONALITY_PHRASES["api_goo  == "ok":
                personality["details"].append(random.choice(PERSONALITY_PHRASES["api_good"]))
            elif results["api"]["status"] in ["error", "warning"]:
                personality["details"].append(random.choice(PERSONALITY_PHRASES["api_bad"]))
        
        if "data_files" in results:
            if results["data_files"]["status"] == "ok":
                personality["details"].append(random.choice(PERSONALITY_PHRASES["data_good"]))
            elif results["data_files"]["status"] in ["error", "warning"]:
                personality["details"].append(random.choice(PERSONALITY_PHRASES["data_bad"]))
        
        # Add a random recommendation
        personality["details"].append(random.choice(PERSONALITY_PHRASES["recommendation"]))
        
        return personality

def print_health_check_results(results: Dict[str, Any], use_color: bool = True, use_personality: bool = True):
    """
    Print health check results in a readable format
    
    Args:
        results: Health check results
        use_color: Whether to use color in output
        use_personality: Whether to use personality in output
    """
    if not use_color:
        # Disable colors
        for color in COLORS:
            COLORS[color] = ""
    
    # Print header
    print(f"\n{COLORS['bold']}🚛 DeepCAL++ System Health Check{COLORS['reset']}")
    print(f"Timestamp: {results['timestamp']}")
    
    # Print personality intro if enabled
    if use_personality and "personality" in results:
        print(f"\n{COLORS['cyan']}🧠 DeepCAL++ says:{COLORS['reset']}")
        print(f"{COLORS['cyan']}\"{results['personality']['intro']}\"{COLORS['reset']}\n")
    
    # Print overall status
    status_colors = {
        "ok": COLORS['green'],
        "warning": COLORS['yellow'],
        "error": COLORS['red'],
        "skipped": COLORS['blue']
    }
    
    overall_status = results["overall_status"].upper()
    status_color = status_colors.get(results["overall_status"], "")
    print(f"Overall Status: {status_color}{overall_status}{COLORS['reset']}")
    print(f"Execution Time: {results['execution_time_ms']} ms\n")
    
    # Print test mode warning if enabled
    if results.get("test_mode", False):
        print(f"{COLORS['yellow']}⚠️ TEST MODE ENABLED: Some failures are simulated{COLORS['reset']}\n")
    
    # Environment
    env = results["environment"]
    env_status = env["status"].upper()
    env_color = status_colors.get(env["status"], "")
    print(f"Environment: {env_color}{env_status}{COLORS['reset']}")
    print(f"  Message: {env['message']}")
    print("  Required Variables:")
    for var, present in env["required"].items():
        status_symbol = "✓" if present else "✗"
        var_color = COLORS['green'] if present else COLORS['red']
        print(f"    {var}: {var_color}{status_symbol}{COLORS['reset']}")
    print()
    
    # Data Files
    data = results["data_files"]
    data_status = data["status"].upper()
    data_color = status_colors.get(data["status"], "")
    print(f"Data Files: {data_color}{data_status}{COLORS['reset']}")
    print(f"  Message: {data['message']}")
    print("  Base Data Files:")
    for file, info in data["base_data"].items():
        status_symbol = "✓" if info['exists'] else "✗"
        file_color = COLORS['green'] if info['exists'] else COLORS['red']
        print(f"    {file}: {file_color}{status_symbol}{COLORS['reset']} ({info['size_kb']} KB)")
    print("  Training Data Files:")
    for file, info in data["training_data"].items():
        status_symbol = "✓" if info['exists'] else "✗"
        file_color = COLORS['green'] if info['exists'] else COLORS['red']
        print(f"    {file}: {file_color}{status_symbol}{COLORS['reset']} ({info['size_kb']} KB)")
    print()
    
    # Core Engine
    engine = results["core_engine"]
    engine_status = engine["status"].upper()
    engine_color = status_colors.get(engine["status"], "")
    print(f"Core Engine: {engine_color}{engine_status}{COLORS['reset']}")
    print(f"  Message: {engine['message']}")
    if "data_loading" in engine["tests"]:
        dl = engine["tests"]["data_loading"]
        status_symbol = "✓" if dl['success'] else "✗"
        dl_color = COLORS['green'] if dl['success'] else COLORS['red']
        print(f"  Data Loading: {dl_color}{status_symbol}{COLORS['reset']}")
        if dl['success']:
            print(f"    Forwarders: {dl['forwarders_count']}")
            print(f"    Load Time: {dl['load_time_ms']} ms")
    if "data_mirror" in engine["tests"]:
        dm = engine["tests"]["data_mirror"]
        status_symbol = "✓" if dm['success'] else "✗"
        dm_color = COLORS['green'] if dm['success'] else COLORS['red']
        print(f"  Data Mirror: {dm_color}{status_symbol}{COLORS['reset']}")
        if dm['success'] and "cache_size" in dm:
            print(f"    Cache Size: {sum(dm['cache_size'].values())} items")
            print(f"    Last Sync: {datetime.fromtimestamp(dm['last_sync']).isoformat() if dm['last_sync'] > 0 else 'Never'}")
    print()
    
    # Supabase
    if "supabase" in results:
        supabase = results["supabase"]
        supabase_status = supabase["status"].upper()
        supabase_color = status_colors.get(supabase["status"], "")
        print(f"Supabase: {supabase_color}{supabase_status}{COLORS['reset']}")
        print(f"  Message: {supabase['message']}")
        if "latency_ms" in supabase:
            print(f"  Latency: {supabase['latency_ms']} ms")
        if "tables" in supabase:
            print("  Tables:")
            for table, info in supabase["tables"].items():
                status_symbol = "✓" if info.get('accessible', False) else "✗"
                table_color = COLORS['green'] if info.get('accessible', False) else COLORS['red']
                print(f"    {table}: {table_color}{status_symbol}{COLORS['reset']}")
                if info.get('accessible', False) and "count" in info:
                    print(f"      Count: {info['count']}")
        print()
    
    # API
    if "api" in results:
        api = results["api"]
        api_status = api["status"].upper()
        api_color = status_colors.get(api["status"], "")
        print(f"API Endpoints: {api_color}{api_status}{COLORS['reset']}")
        print(f"  Message: {api['message']}")
        if "endpoints" in api:
            for endpoint, info in api["endpoints"].items():
                status_symbol = "✓" if info.get('accessible', False) else "✗"
                endpoint_color = COLORS['green'] if info.get('accessible', False) else COLORS['red']
                print(f"  /{endpoint}: {endpoint_color}{status_symbol}{COLORS['reset']}")
                if "latency_ms" in info:
                    print(f"    Latency: {info['latency_ms']} ms")
                if "forwarders_count" in info:
                    print(f"    Forwarders: {info['forwarders_count']}")
        print()
    
    # Voice
    if "voice" in results:
        voice = results["voice"]
        voice_status = voice["status"].upper()
        voice_color = status_colors.get(voice["status"], "")
        print(f"Voice System: {voice_color}{voice_status}{COLORS['reset']}")
        print(f"  Message: {voice['message']}")
        status_symbol = "✓" if voice['available'] else "✗"
        voice_avail_color = COLORS['green'] if voice['available'] else COLORS['yellow']
        print(f"  Available: {voice_avail_color}{status_symbol}{COLORS['reset']}")
        print()
    
    # Logs
    if "logs" in results:
        logs = results["logs"]
        logs_status = logs["status"].upper()
        logs_color = status_colors.get(logs["status"], "")
        print(f"Logs: {logs_color}{logs_status}{COLORS['reset']}")
        print(f"  Message: {logs['message']}")
        if "log_file" in logs and logs["log_file"].get("exists", False):
            print(f"  Log File: {LOG_FILE_PATH}")
            print(f"  Size: {logs['log_file']['size_kb']} KB")
            print(f"  Last Modified: {logs['log_file']['last_modified']}")
            status_symbol = "✓" if logs["log_file"].get("writable", False) else "✗"
            writable_color = COLORS['green'] if logs["log_file"].get("writable", False) else COLORS['red']
            print(f"  Writable: {writable_color}{status_symbol}{COLORS['reset']}")
        print()
    
    # Print personality conclusion if enabled
    if use_personality and "personality" in results:
        print(f"{COLORS['cyan']}🧠 DeepCAL++ concludes:{COLORS['reset']}")
        print(f"{COLORS['cyan']}\"{results['personality']['conclusion']}\"{COLORS['reset']}\n")
        
        if results["personality"]["details"]:
            print(f"{COLORS['cyan']}Additional insights:{COLORS['reset']}")
            for detail in results["personality"]["details"]:
                print(f"{COLORS['cyan']}• {detail}{COLORS['reset']}")
            print()

def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description="DeepCAL++ Health Check")
    parser.add_argument("--no-supabase", action="store_true", help="Skip Supabase connection check")
    parser.add_argument("--no-voice", action="store_true", help="Skip voice system check")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--no-personality", action="store_true", help="Disable personality in output")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    parser.add_argument("--save", help="Save results to file")
    parser.add_argument("--test", action="store_true", help="Run in test mode (simulate failures)")
    parser.add_argument("--test-scenario", choices=["supabase_down", "api_down", "data_corrupt", 
                                                  "engine_failure", "voice_unavailable", "env_missing"], 
                       help="Specific test scenario to simulate")
    parser.add_argument("--speak", action="store_true", help="Speak the results summary using voice system")
    
    args = parser.parse_args()
    
    # Run health check
    health_check = HealthCheck(
        check_supabase=not args.no_supabase,
        check_voice=not args.no_voice,
        test_mode=args.test,
        test_scenario=args.test_scenario
    )
    
    results = health_check.run_all_checks()
    
    # Save results if requested
    if args.save:
        with open(args.save, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.save}")
    
    # Output results
    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print_health_check_results(results, use_color=not args.no_color, use_personality=not args.no_personality)
    
    # Speak results if requested
    if args.speak and not args.no_voice and results.get("voice", {}).get("available", False):
        try:
            # Generate speech text
            speech_text = f"DeepCAL++ health check complete. Overall status: {results['overall_status']}."
            
            if "personality" in results:
                speech_text += f" {results['personality']['conclusion']}"
            
            # Add details for non-ok components
            for component_name, component in results.items():
                if isinstance(component, dict) and "status" in component and component["status"] not in ["ok", "skipped"]:
                    speech_text += f" {component_name} status: {component['status']}. {component['message']}."
            
            # Speak the text
            speak_text(speech_text, blocking=True)
        except Exception as e:
            print(f"Error speaking results: {e}")
    
    # Return exit code based on status
    return 0 if results["overall_status"] == "ok" else 1

if __name__ == "__main__":
    sys.exit(main())


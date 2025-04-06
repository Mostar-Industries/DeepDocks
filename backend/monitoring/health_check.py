#!/usr/bin/env python
"""
DeepCAL++ Health Check Module
This module provides system health monitoring functionality
"""
import os
import sys
import json
import time
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple
import requests

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(parent_dir)

# Import required modules
from backend.data.data_mirror import get_data_mirror
from backend.core.deepcal_core import load_forwarders_for_route
from backend.voice.speak import check_voice_availability

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("health_check")

class HealthCheck:
    """
    System health check functionality for DeepCAL++
    """
    def __init__(self, check_supabase: bool = True, check_voice: bool = True):
        """
        Initialize health check
        
        Args:
            check_supabase: Whether to check Supabase connectivity
            check_voice: Whether to check voice system
        """
        self.check_supabase = check_supabase
        self.check_voice = check_voice
        self.data_mirror = get_data_mirror()
        
        # Load environment variables
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.api_key = os.getenv("DEEPCAL_API_KEY")
        self.data_directory = os.getenv("DATA_DIRECTORY", "backend/data")
        
    def check_environment(self) -> Dict[str, Any]:
        """
        Check environment variables
        
        Returns:
            Dictionary with environment check results
        """
        required_vars = ["DEEPCAL_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
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
        base_data_dir = os.path.join(parent_dir, self.data_directory, "base_data")
        if not os.path.exists(base_data_dir):
            data_status["status"] = "warning"
            data_status["message"] = f"Base data directory not found: {base_data_dir}"
            return data_status
        
        # Check base data files
        base_files = ["forwarders.json", "routes.json", "rate_cards.json", "shipments.json"]
        for file in base_files:
            file_path = os.path.join(base_data_dir, file)
            exists = os.path.exists(file_path)
            data_status["base_data"][file] = {
                "exists": exists,
                "size_kb": round(os.path.getsize(file_path) / 1024, 2) if exists else 0,
                "last_modified": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat() if exists else None
            }
        
        # Check training data directory
        training_data_dir = os.path.join(parent_dir, self.data_directory, "training_data")
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
                "last_modified": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat() if exists else None
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
        
        # Check Supabase connection
        try:
            # Simple health check request to Supabase
            headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}"
            }
            
            # Check forwarders table
            response = requests.get(
                f"{self.supabase_url}/rest/v1/forwarders?select=count",
                headers=headers
            )
            
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
        
        # Test data loading
        try:
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
    
    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all health checks
        
        Returns:
            Dictionary with all health check results
        """
        start_time = time.time()
        
        results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "environment": self.check_environment(),
            "data_files": self.check_data_files(),
            "core_engine": self.check_core_engine(),
            "overall_status": "ok"
        }
        
        # Add Supabase check if enabled
        if self.check_supabase:
            results["supabase"] = self.check_supabase_connection()
        
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
        
        return results

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DeepCAL++ Health Check")
    parser.add_argument("--no-supabase", action="store_true", help="Skip Supabase connection check")
    parser.add_argument("--no-voice", action="store_true", help="Skip voice system check")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")
    parser.add_argument("--save", help="Save results to file")
    
    args = parser.parse_args()
    
    # Run health check
    health_check = HealthCheck(
        check_supabase=not args.no_supabase,
        check_voice=not args.no_voice
    )
    
    results = health_check.run_all_checks()
    
    # Save results if requested
    if args.save:
        with open(args.save, "w") as f:
            json.dump(results, f, indent=2)
    
    # Output results
    if args.output == "json":
        print(json.dumps(results, indent=2))
    else:
        print("\n=== DeepCAL++ Health Check Results ===")
        print(f"Timestamp: {results['timestamp']}")
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(f"Execution Time: {results['execution_time_ms']} ms\n")
        
        # Environment
        env = results["environment"]
        print(f"Environment: {env['status'].upper()}")
        print(f"  Message: {env['message']}")
        print("  Required Variables:")
        for var, present in env["required"].items():
            print(f"    {var}: {'✓' if present else '✗'}")
        print()
        
        # Data Files
        data = results["data_files"]
        print(f"Data Files: {data['status'].upper()}")
        print(f"  Message: {data['message']}")
        print("  Base Data Files:")
        for file, info in data["base_data"].items():
            print(f"    {file}: {'✓' if info['exists'] else '✗'} ({info['size_kb']} KB)")
        print("  Training Data Files:")
        for file, info in data["training_data"].items():
            print(f"    {file}: {'✓' if info['exists'] else '✗'} ({info['size_kb']} KB)")
        print()
        
        # Core Engine
        engine = results["core_engine"]
        print(f"Core Engine: {engine['status'].upper()}")
        print(f"  Message: {engine['message']}")
        if "data_loading" in engine["tests"]:
            dl = engine["tests"]["data_loading"]
            print(f"  Data Loading: {'✓' if dl['success'] else '✗'}")
            if dl['success']:
                print(f"    Forwarders: {dl['forwarders_count']}")
                print(f"    Load Time: {dl['load_time_ms']} ms")
        if "data_mirror" in engine["tests"]:
            dm = engine["tests"]["data_mirror"]
            print(f"  Data Mirror: {'✓' if dm['success'] else '✗'}")
            if dm['success'] and "cache_size" in dm:
                print(f"    Cache Size: {sum(dm['cache_size'].values())} items")
                print(f"    Last Sync: {datetime.datetime.fromtimestamp(dm['last_sync']).isoformat() if dm['last_sync'] > 0 else 'Never'}")
        print()
        
        # Supabase
        if "supabase" in results:
            supabase = results["supabase"]
            print(f"Supabase: {supabase['status'].upper()}")
            print(f"  Message: {supabase['message']}")
            if "tables" in supabase:
                print("  Tables:")
                for table, info in supabase["tables"].items():
                    print(f"    {table}: {'✓' if info.get('accessible', False) else '✗'}")
                    if info.get('accessible', False) and "count" in info:
                        print(f"      Count: {info['count']}")
            print()
        
        # Voice
        if "voice" in results:
            voice = results["voice"]
            print(f"Voice System: {voice['status'].upper()}")
            print(f"  Message: {voice['message']}")
            print(f"  Available: {'✓' if voice['available'] else '✗'}")
            print()

if __name__ == "__main__":
    main()


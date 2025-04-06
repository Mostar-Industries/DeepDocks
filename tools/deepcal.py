#!/usr/bin/env python
"""
DeepCAL++ CLI Tool
This script provides a command-line interface for DeepCAL++ operations
"""
import os
import sys
import argparse
import json
import subprocess
from datetime import datetime

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(parent_dir)

def check_status(args):
    """Run health check"""
    from backend.cli.check_status import HealthCheck
    
    health_check = HealthCheck(
        check_supabase=not args.no_supabase,
        check_voice=not args.no_voice,
        test_mode=args.test,
        test_scenario=args.test_scenario
    )
    
    results = health_check.run_all_checks()
    
    # Save results if requested
    if args.save:
        save_path = args.save
        if save_path == "auto":
            os.makedirs("logs", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"logs/health_check_{timestamp}.json"
        
        with open(save_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {save_path}")
    
    # Output results
    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        from backend.cli.check_status import print_health_check_results
        print_health_check_results(results, use_color=not args.no_color, use_personality=not args.no_personality)
    
    # Speak results if requested
    if args.speak and not args.no_voice:
        try:
            from backend.voice.speak import speak_text, check_voice_availability
            
            if check_voice_availability():
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
            else:
                print("Voice system is not available")
        except Exception as e:
            print(f"Error speaking results: {e}")
    
    # Return exit code based on status
    return 0 if results["overall_status"] == "ok" else 1

def run_cron_check(args):
    """Run cron health check"""
    # Run the cron health check script
    cron_script = os.path.join(parent_dir, "backend", "cli", "cron_health_check.py")
    
    cmd = [sys.executable, cron_script]
    
    try:
        subprocess.run(cmd, check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Cron health check failed with exit code {e.returncode}")
        return e.returncode

def test_api(args):
    """Test API endpoints"""
    print("Testing API endpoints...")
    
    # Test rank API
    if args.endpoint == "rank" or args.endpoint == "all":
        test_rank_api()
    
    # Test mirror-data API
    if args.endpoint == "mirror-data" or args.endpoint == "all":
        test_mirror_data_api()
    
    # Test health API
    if args.endpoint == "health" or args.endpoint == "all":
        test_health_api()
    
    return 0

def test_rank_api():
    """Test the rank API endpoint"""
    import requests
    
    print("\nTesting /api/rank endpoint...")
    
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
    
    # Determine API URL
    api_url = os.getenv("DEEPCAL_API_URL", "http://localhost:3000/api/rank")
    
    try:
        # Make request
        response = requests.post(
            api_url,
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("✓ Rank API test successful")
            print(f"  Results: {len(result.get('results', []))} forwarders ranked")
            print(f"  Top forwarder: {result.get('results', [{}])[0].get('name', 'Unknown')}")
            print(f"  Response time: {response.elapsed.total_seconds() * 1000:.2f} ms")
        else:
            print(f"✗ Rank API test failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Rank API test failed: {str(e)}")

def test_mirror_data_api():
    """Test the mirror-data API endpoint"""
    import requests
    
    print("\nTesting /api/mirror-data endpoint...")
    
    # Prepare test data
    test_data = {
        "forwarders": [
            {
                "id": "test-f1",
                "name": "Test Forwarder",
                "country": "Test Country",
                "region": "Test Region"
            }
        ],
        "routes": [
            {
                "id": "test-r1",
                "origin_country": "Test Origin",
                "destination_country": "Test Destination"
            }
        ],
        "rate_cards": [],
        "forwarder_services": [],
        "performance_analytics": [],
        "shipments": []
    }
    
    # Determine API URL
    api_url = os.getenv("DEEPCAL_API_URL", "http://localhost:3000/api/mirror-data")
    api_key = os.getenv("DEEPCAL_API_KEY", "")
    
    if not api_key:
        print("✗ Mirror-data API test skipped: DEEPCAL_API_KEY not set")
        return
    
    try:
        # Make request
        response = requests.post(
            api_url,
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("✓ Mirror-data API test successful")
            print(f"  Message: {result.get('message', 'Unknown')}")
            print(f"  Response time: {response.elapsed.total_seconds() * 1000:.2f} ms")
        else:
            print(f"✗ Mirror-data API test failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Mirror-data API test failed: {str(e)}")

def test_health_api():
    """Test the health API endpoint"""
    import requests
    
    print("\nTesting /api/health endpoint...")
    
    # Determine API URL
    api_url = os.getenv("DEEPCAL_API_URL", "http://localhost:3000/api/health")
    api_key = os.getenv("DEEPCAL_API_KEY", "")
    
    if not api_key:
        print("✗ Health API test skipped: DEEPCAL_API_KEY not set")
        return
    
    try:
        # Make request
        response = requests.get(
            api_url,
            headers={
                "Authorization": f"Bearer {api_key}"
            }
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("✓ Health API test successful")
            print(f"  Status: {result.get('overall_status', 'Unknown')}")
            print(f"  Response time: {response.elapsed.total_seconds() * 1000:.2f} ms")
        else:
            print(f"✗ Health API test failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Health API test failed: {str(e)}")

def run_voice_test(args):
    """Run voice system test"""
    print("Testing voice system...")
    
    # Run the voice test script
    voice_test_script = os.path.join(parent_dir, "tools", "test_voice.py")
    
    cmd = [sys.executable, voice_test_script]
    if args.text:
        cmd.extend(["--text", args.text])
    if args.stats:
        cmd.append("--stats")
    
    try:
        subprocess.run(cmd, check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Voice test failed with exit code {e.returncode}")
        return e.returncode

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="DeepCAL++ CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Check status command
    check_parser = subparsers.add_parser("check", help="Check system status")
    check_subparsers = check_parser.add_subparsers(dest="check_command", help="Check command to run")
    
    # Status check command
    status_parser = check_subparsers.add_parser("status", help="Check system status")
    status_parser.add_argument("--no-supabase", action="store_true", help="Skip Supabase connection check")
    status_parser.add_argument("--no-voice", action="store_true", help="Skip voice system check")
    status_parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    status_parser.add_argument("--no-personality", action="store_true", help="Disable personality in output")
    status_parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    status_parser.add_argument("--save", help="Save results to file (use 'auto' for automatic filename)")
    status_parser.add_argument("--test", action="store_true", help="Run in test mode (simulate failures)")
    status_parser.add_argument("--test-scenario", choices=["supabase_down", "api_down", "data_corrupt", 
                                                         "engine_failure", "voice_unavailable", "env_missing"], 
                              help="Specific test scenario to simulate")
    status_parser.add_argument("--speak", action="store_true", help="Speak the results summary using voice system")
    status_parser.set_defaults(func=check_status)
    
    # Cron check command
    cron_parser = check_subparsers.add_parser("cron", help="Run scheduled health check for cron")
    cron_parser.set_defaults(func=run_cron_check)
    
    # Test API command
    test_parser = subparsers.add_parser("test-api", help="Test API endpoints")
    test_parser.add_argument("--endpoint", choices=["rank", "mirror-data", "health", "all"], default="all", help="Endpoint to test")
    test_parser.set_defaults(func=test_api)
    
    # Voice test command
    voice_parser = subparsers.add_parser("test-voice", help="Test voice system")
    voice_parser.add_argument("--text", default="This is a test of the DeepCAL++ voice system.", help="Text to speak")
    voice_parser.add_argument("--stats", action="store_true", help="Show voice usage statistics")
    voice_parser.set_defaults(func=run_voice_test)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Run the selected command
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())


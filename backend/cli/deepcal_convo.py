#!/usr/bin/env python
"""
DeepCAL++ CLI Conversation Interface
This module provides a command-line interface for interacting with the DeepCAL++ system via voice
"""
import os
import sys
import argparse
import time
from typing import Dict, List, Any, Optional

# Add parent directory to path to allow importing from sibling packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from voice.speak import speak_text, check_voice_availability
from voice.audio_preprocessor import record_and_transcribe, check_audio_availability
from core.deepcal_core import process_logistics_data, run_topsis_analysis
from commentary.commentary import generate_commentary, generate_voice_summary

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_color(text: str, color: str = 'reset'):
    """Print colored text to the terminal"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'reset': '\033[0m'
    }
    
    print(f"{colors.get(color, colors['reset'])}{text}{colors['reset']}")

def print_banner():
    """Print the DeepCAL++ CLI banner"""
    banner = """
    ██████╗ ███████╗███████╗██████╗  ██████╗ █████╗ ██╗     ██╗██╗
    ██╔══██╗██╔════╝██╔════╝██╔══██╗██╔════╝██╔══██╗██║     ██║╚██╗
    ██║  ██║█████╗  █████╗  ██████╔╝██║     ███████║██║     ██║ ╚██╗
    ██║  ██║██╔══╝  ██╔══╝  ██╔═══╝ ██║     ██╔══██║██║     ██║ ██╔╝
    ██████╔╝███████╗███████╗██║     ╚██████╗██║  ██║███████╗██║██╔╝ 
    ╚═════╝ ╚══════╝╚══════╝╚═╝      ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  
                                                       
     African Logistics Decision Support System - Voice Interface
    """
    print_color(banner, 'green')
    print_color("\n Welcome to DeepCAL++ Voice Interface\n", 'cyan')
    print_color(" Say 'help' at any time for assistance or 'exit' to quit\n", 'yellow')
    print("="*80 + "\n")

def handle_command(command: str) -> Dict[str, Any]:
    """
    Process a voice command
    
    Args:
        command: Voice command text
        
    Returns:
        Command result
    """
    # Convert to lowercase and strip whitespace
    command = command.lower().strip()
    
    # Check for exit command
    if command in ['exit', 'quit', 'goodbye', 'bye']:
        return {
            'action': 'exit',
            'message': 'Goodbye! Thank you for using DeepCAL++.',
            'speak': 'Goodbye! Thank you for using DeepCAL++'
        }
    
    # Check for help command
    if command in ['help', 'instructions', 'commands']:
        help_text = """
        Available Commands:
        ------------------
        'compare forwarders' - Start a forwarder comparison analysis
        'predict delivery' - Predict delivery time for a shipment
        'explain last result' - Get a detailed explanation of the last analysis
        'help' - Show this help message
        'exit' or 'quit' - Exit the program
        """
        
        speak_text = "Available commands include: compare forwarders, predict delivery, explain last result, help, and exit."
        
        return {
            'action': 'help',
            'message': help_text,
            'speak': speak_text
        }
    
    # Check for analysis commands
    if any(x in command for x in ['compare', 'analysis', 'rank']):
        return {
            'action': 'compare',
            'message': "Starting forwarder comparison analysis...",
            'speak': "I'll help you compare logistics forwarders. Let me ask you a few questions."
        }
    
    # Check for prediction commands
    if any(x in command for x in ['predict', 'forecast', 'estimate']):
        return {
            'action': 'predict',
            'message': "Starting delivery prediction...",
            'speak': "I'll help you predict delivery time. Let me ask you a few questions."
        }
    
    # Check for explanation command
    if any(x in command for x in ['explain', 'details', 'why']):
        return {
            'action': 'explain',
            'message': "Generating detailed explanation...",
            'speak': "Let me explain the analysis results in more detail."
        }
    
    # Default response for unknown command
    return {
        'action': 'unknown',
        'message': f"Sorry, I didn't understand '{command}'. Try saying 'help' for available commands.",
        'speak': "Sorry, I didn't understand that command. Try saying help for available commands."
    }

def listen_for_command() -> Dict[str, Any]:
    """
    Listen for a voice command
    
    Returns:
        Command text or error
    """
    print_color("\nListening for command...", 'yellow')
    
    if not check_audio_availability():
        print_color("Audio input not available. Please type your command:", 'red')
        command = input("> ")
        return {'success': True, 'text': command}
    
    # Record and transcribe
    transcription = record_and_transcribe(duration=5)
    
    if not transcription['success']:
        print_color(f"Error: {transcription.get('error', 'Unknown error')}", 'red')
        print_color("Please type your command:", 'yellow')
        command = input("> ")
        return {'success': True, 'text': command}
    
    print_color(f"Heard: {transcription['text']}", 'green')
    return transcription

def run_forwarder_comparison() -> Dict[str, Any]:
    """
    Run an interactive forwarder comparison
    
    Returns:
        Analysis results
    """
    print_color("\nForwarder Comparison", 'cyan')
    speak_text("Let's compare logistics forwarders. I'll need some information.", blocking=True)
    
    # Collect information for three forwarders
    forwarders = []
    
    for i in range(3):
        print_color(f"\nForwarder {i+1}", 'magenta')
        speak_text(f"Let's get the details for forwarder {i+1}", blocking=True)
        
        # Default forwarder data
        default_names = ["AfricaLogistics", "GlobalFreight", "ExpressShip"]
        default_costs = [1200, 950, 1450]
        default_times = [14, 18, 10]
        default_reliability = [85, 78, 92]
        default_tracking = [True, False, True]
        
        print(f"Name (default: {default_names[i]}): ", end="")
        speak_text(f"What is the name of forwarder {i+1}?", blocking=True)
        name = input()
        name = name if name else default_names[i]
        
        print(f"Cost in USD (default: {default_costs[i]}): ", end="")
        speak_text(f"What is the cost for {name}?", blocking=True)
        cost_input = input()
        cost = int(cost_input) if cost_input else default_costs[i]
        
        print(f"Delivery time in days (default: {default_times[i]}): ", end="")
        speak_text(f"How many days for delivery?", blocking=True)
        time_input = input()
        time = int(time_input) if time_input else default_times[i]
        
        print(f"Reliability score 0-100 (default: {default_reliability[i]}): ", end="")
        speak_text(f"What is the reliability score from 0 to 100?", blocking=True)
        reliability_input = input()
        reliability = int(reliability_input) if reliability_input else default_reliability[i]
        
        print(f"Real-time tracking available (y/n) (default: {'y' if default_tracking[i] else 'n'}): ", end="")
        speak_text(f"Does {name} offer real-time tracking?", blocking=True)
        tracking_input = input().lower()
        if tracking_input:
            tracking = tracking_input.startswith('y')
        else:
            tracking = default_tracking[i]
        
        forwarders.append({
            "name": name,
            "cost": cost,
            "time": time,
            "reliability": reliability,
            "tracking": tracking
        })
    
    # Process the data
    print_color("\nAnalyzing forwarders...", 'yellow')
    speak_text("Analyzing the forwarders.", blocking=True)
    
    processed_data = process_logistics_data(forwarders)
    results = run_topsis_analysis(processed_data, analysis_depth=4)
    
    # Generate voice summary
    voice_summary = generate_voice_summary(results)
    speak_text(voice_summary, blocking=False)
    
    # Display results
    print_color("\nAnalysis Results", 'cyan')
    print("\nRanking:")
    for result in results:
        print(f"{result['rank']}. {result['name']} - Score: {result['score']:.3f}")
    
    print("\nRecommendation:")
    print_color(f"The recommended forwarder is {results[0]['name']} with a score of {results[0]['score']:.3f}", 'green')
    
    return {
        'action': 'analysis_complete',
        'results': results,
        'forwarders': forwarders
    }

def generate_explanation(results: List[Dict[str, Any]], forwarders: List[Dict[str, Any]]) -> None:
    """Generate and display a detailed explanation"""
    print_color("\nGenerating detailed explanation...", 'yellow')
    
    commentary = generate_commentary(results, forwarders)
    
    print_color("\nDetailed Analysis", 'cyan')
    print(commentary)
    
    # Generate a shorter version for voice
    voice_commentary = f"""
    Based on our analysis, {results[0]['name']} is the recommended option with a score of {results[0]['score']:.2f}.
    
    It offers a good balance of cost, delivery time, and reliability. Compared to the second option, 
    {results[1]['name']}, it performs better overall in the most important factors for your shipment.
    
    If you'd like more details on specific factors such as cost efficiency or delivery time
    comparisons, please let me know.
    """
    
    speak_text(voice_commentary, blocking=True)

def main():
    """Main CLI function"""
    # Check voice availability
    voice_available = check_voice_availability()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='DeepCAL++ Voice Interface')
    parser.add_argument('--no-voice', action='store_true', help='Disable voice output')
    args = parser.parse_args()
    
    # Override voice based on arguments
    if args.no_voice:
        voice_available = False
    
    # Welcome message
    clear_screen()
    print_banner()
    
    if voice_available:
        speak_text("Welcome to DeepCAL++ Voice Interface. How can I help you today?", blocking=True)
    
    # Store latest analysis results
    last_results = None
    last_forwarders = None
    
    # Main interaction loop
    running = True
    while running:
        # Get command
        transcription = listen_for_command()
        
        if not transcription['success']:
            print_color("Sorry, I couldn't understand. Please try again.", 'red')
            continue
        
        # Process command
        command_text = transcription['text']
        result = handle_command(command_text)
        
        # Print response
        print_color(result['message'], 'cyan')
        
        # Speak response if voice is available
        if voice_available and 'speak' in result:
            speak_text(result['speak'], blocking=True)
        
        # Handle actions
        if result['action'] == 'exit':
            running = False
        elif result['action'] == 'compare':
            analysis_result = run_forwarder_comparison()
            last_results = analysis_result['results']
            last_forwarders = analysis_result['forwarders']
        elif result['action'] == 'explain':
            if last_results and last_forwarders:
                generate_explanation(last_results, last_forwarders)
            else:
                print_color("No analysis results available. Please run a comparison first.", 'red')
                if voice_available:
                    speak_text("No analysis results available. Please run a comparison first.", blocking=True)
        
        # Pause briefly
        if running:
            time.sleep(1)
    
    print_color("\nThank you for using DeepCAL++. Goodbye!", 'green')

if __name__ == "__main__":
    main()


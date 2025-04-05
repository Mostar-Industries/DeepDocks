#!/usr/bin/env python
"""
DeepCAL++ Voice Command Testing Tool
This script tests the voice recognition and command processing functionality
"""
import os
import sys
import time
from typing import Dict, Any, List

# Add parent directory to path to allow importing from sibling packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from voice.speak import speak_text, check_voice_availability
from voice.audio_preprocessor import record_and_transcribe, check_audio_availability

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
    """Print the DeepCAL++ Voice Testing banner"""
    banner = """
    ██████╗ ███████╗███████╗██████╗  ██████╗ █████╗ ██╗     ██╗██╗
    ██╔══██╗██╔════╝██╔════╝██╔══██╗██╔════╝██╔══██╗██║     ██║╚██╗
    ██║  ██║█████╗  █████╗  ██████╔╝██║     ███████║██║     ██║ ╚██╗
    ██║  ██║██╔══╝  ██╔══╝  ██╔═══╝ ██║     ██╔══██║██║     ██║ ██╔╝
    ██████╔╝███████╗███████╗██║     ╚██████╗██║  ██║███████╗██║██╔╝ 
    ╚═════╝ ╚══════╝╚══════╝╚═╝      ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  
                                                       
     Voice Command Testing Tool
    """
    print_color(banner, 'cyan')
    print_color("\n This tool tests voice recognition and command processing.\n", 'yellow')
    print("="*80 + "\n")

def test_voice_output():
    """Test the text-to-speech functionality"""
    print_color("Testing voice output...", 'yellow')
    
    if not check_voice_availability():
        print_color("Voice output is not available on this system.", 'red')
        return False
    
    print_color("Voice output is available.", 'green')
    
    # Test different voice types
    voices = ["default", "male", "female"]
    for voice in voices:
        print_color(f"Testing {voice} voice...", 'yellow')
        speak_text(f"This is a test of the {voice} voice for DeepCAL++.", voice_type=voice, blocking=True)
        time.sleep(0.5)
    
    # Test different speeds
    speeds = [0.8, 1.0, 1.5]
    for speed in speeds:
        print_color(f"Testing speech rate {speed}...", 'yellow')
        speak_text(f"This is a test at {speed} times normal speed.", speed=speed, blocking=True)
        time.sleep(0.5)
    
    print_color("Voice output test complete.", 'green')
    return True

def test_voice_input():
    """Test the speech recognition functionality"""
    print_color("Testing voice input...", 'yellow')
    
    if not check_audio_availability():
        print_color("Voice input is not available on this system.", 'red')
        return False
    
    print_color("Voice input is available.", 'green')
    
    # Simple listening test
    print_color("I'll listen for 5 seconds. Please say something...", 'yellow')
    speak_text("I'll listen for 5 seconds. Please say something.", blocking=True)
    
    transcription = record_and_transcribe(duration=5)
    
    if transcription['success']:
        print_color(f"Heard: {transcription['text']}", 'green')
        speak_text(f"I heard: {transcription['text']}", blocking=True)
        return True
    else:
        print_color(f"Error: {transcription.get('error', 'Unknown error')}", 'red')
        speak_text("I couldn't understand what you said.", blocking=True)
        return False

def test_command_recognition():
    """Test command recognition"""
    print_color("Testing command recognition...", 'yellow')
    
    # Define test commands
    test_commands = [
        "compare forwarders",
        "predict delivery time",
        "explain the results",
        "help me",
        "exit"
    ]
    
    # Print commands for user to try
    print_color("Please try saying the following commands:", 'cyan')
    for i, cmd in enumerate(test_commands):
        print(f"{i+1}. {cmd}")
    
    speak_text("Let's test command recognition. I'll listen for each command you say.", blocking=True)
    
    # Test each command
    for i, cmd in enumerate(test_commands):
        print_color(f"\nPlease say: '{cmd}'", 'yellow')
        speak_text(f"Please say: {cmd}", blocking=True)
        
        if not check_audio_availability():
            print_color("Voice input not available. Please type the command:", 'red')
            heard = input("> ")
            success = True
        else:
            # Listen for command
            transcription = record_and_transcribe(duration=5)
            success = transcription['success']
            heard = transcription.get('text', "") if success else ""
        
        # Check if command was recognized
        if success:
            print_color(f"Heard: {heard}", 'green')
            
            # Simple command comparison (could be more sophisticated)
            cmd_keywords = cmd.lower().split()
            heard_keywords = heard.lower().split()
            
            matches = any(k in heard_keywords for k in cmd_keywords)
            
            if matches:
                print_color("Command recognized! ✅", 'green')
                speak_text("Command recognized.", blocking=True)
            else:
                print_color("Command not recognized. ❌", 'red')
                speak_text("Command not recognized.", blocking=True)
        else:
            print_color("Failed to capture audio.", 'red')
            speak_text("Failed to capture audio.", blocking=True)
        
        time.sleep(1)
    
    print_color("\nCommand recognition test complete.", 'green')
    speak_text("Command recognition test complete.", blocking=True)

def main():
    """Main function"""
    clear_screen()
    print_banner()
    
    # Print system status
    print_color("Checking system capabilities...", 'yellow')
    voice_output_available = check_voice_availability()
    voice_input_available = check_audio_availability()
    
    print_color("System Status:", 'cyan')
    print(f"Voice Output: {'Available ✅' if voice_output_available else 'Not Available ❌'}")
    print(f"Voice Input: {'Available ✅' if voice_input_available else 'Not Available ❌'}")
    print("")
    
    # Test menu
    print_color("Test Menu:", 'cyan')
    print("1. Test Voice Output")
    print("2. Test Voice Input")
    print("3. Test Command Recognition")
    print("4. Run All Tests")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-4): ")
    
    if choice == '1':
        test_voice_output()
    elif choice == '2':
        test_voice_input()
    elif choice == '3':
        test_command_recognition()
    elif choice == '4':
        print_color("\nRunning all tests...", 'yellow')
        voice_ok = test_voice_output()
        input_ok = test_voice_input()
        if voice_ok and input_ok:
            test_command_recognition()
    
    print_color("\nTest complete. Thank you for using the DeepCAL++ Voice Testing Tool!", 'green')

if __name__ == "__main__":
    main()


"""
Test suite for DeepCAL++ voice functionality
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules to test
from backend.voice.speak import (
    speak_text,
    stop_speaking,
    check_voice_availability
)

class TestVoiceFunctionality(unittest.TestCase):
    """Test cases for voice functionality"""
    
    @patch('backend.voice.speak._tts_available', True)
    @patch('backend.voice.speak._voice_engine')
    def test_speak_text(self, mock_engine):
        """Test the speak_text function"""
        # Configure the mock
        mock_engine.set_voice.return_value = True
        mock_engine.set_speed.return_value = True
        mock_engine.speak.return_value = True
        
        # Call the function
        result = speak_text("Hello world", blocking=False)
        
        # Check that the engine methods were called
        mock_engine.set_voice.assert_called_once()
        mock_engine.set_speed.assert_called_once()
        mock_engine.speak.assert_called_once_with("Hello world", False)
        
        # Check the result
        self.assertTrue(result)
    
    @patch('backend.voice.speak._tts_available', True)
    @patch('backend.voice.speak._voice_engine')
    def test_stop_speaking(self, mock_engine):
        """Test the stop_speaking function"""
        # Configure the mock
        mock_engine.stop.return_value = True
        
        # Call the function
        result = stop_speaking()
        
        # Check that the engine method was called
        mock_engine.stop.assert_called_once()
        
        # Check the result
        self.assertTrue(result)
    
    @patch('backend.voice.speak._tts_available', True)
    def test_check_voice_availability_when_available(self):
        """Test the check_voice_availability function when voice is available"""
        result = check_voice_availability()
        self.assertTrue(result)
    
    @patch('backend.voice.speak._tts_available', False)
    def test_check_voice_availability_when_not_available(self):
        """Test the check_voice_availability function when voice is not available"""
        result = check_voice_availability()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()


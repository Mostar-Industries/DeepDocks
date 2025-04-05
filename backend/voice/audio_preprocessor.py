"""
DeepCAL++ Audio Preprocessor
This module provides audio preprocessing functionality for voice input
"""
import os
import sys
import tempfile
from typing import Optional, Tuple, Dict, Any, List

# Try to import audio processing libraries
# These are conditionally imported to handle environments without audio support
try:
    import speech_recognition as sr
    import librosa
    import numpy as np
    _audio_available = True
except ImportError:
    _audio_available = False
    print("Warning: Audio processing libraries not available. Voice input functionality will be limited.")

class AudioPreprocessor:
    """
    Audio preprocessing for voice input in noisy environments
    """
    def __init__(self):
        """Initialize the audio preprocessor"""
        self.recognizer = None
        
        if _audio_available:
            try:
                self.recognizer = sr.Recognizer()
                # Set energy threshold for speech detection
                self.recognizer.energy_threshold = 4000
                # Set dynamic energy threshold to adapt to background noise
                self.recognizer.dynamic_energy_threshold = True
            except Exception as e:
                print(f"Error initializing audio preprocessor: {e}")
    
    def record_audio(self, duration: int = 5) -> Optional[sr.AudioData]:
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            AudioData object or None if recording failed
        """
        if not _audio_available or not self.recognizer:
            print("Audio recording not available")
            return None
        
        try:
            with sr.Microphone() as source:
                print(f"Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                print(f"Recording for {duration} seconds...")
                audio = self.recognizer.record(source, duration=duration)
                return audio
        
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None
    
    def denoise_audio(self, audio_data: sr.AudioData) -> Optional[sr.AudioData]:
        """
        Denoise audio data
        
        Args:
            audio_data: Audio data to denoise
            
        Returns:
            Denoised audio data or None if denoising failed
        """
        if not _audio_available or not self.recognizer:
            return None
        
        try:
            # Convert to numpy array
            raw_data = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
            sample_rate = audio_data.sample_rate
            
            # Simple noise reduction using librosa
            # This is a basic spectral subtraction approach
            # More advanced techniques could be implemented
            y = raw_data.astype(np.float32) / 32768.0
            
            # Apply a high-pass filter to reduce low-frequency noise
            y_filtered = librosa.effects.preemphasis(y)
            
            # Convert back to int16
            filtered_data = (y_filtered * 32768.0).astype(np.int16)
            
            # Create a new AudioData object with the filtered data
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                import wave
                
                with wave.open(temp_file.name, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(sample_rate)
                    wf.writeframes(filtered_data.tobytes())
                
                with sr.AudioFile(temp_file.name) as source:
                    denoised_audio = self.recognizer.record(source)
                
                # Clean up temp file
                os.unlink(temp_file.name)
            
            return denoised_audio
        
        except Exception as e:
            print(f"Error denoising audio: {e}")
            return audio_data  # Return original if denoising fails
    
    def transcribe_audio(
        self, 
        audio_data: sr.AudioData, 
        engine: str = "google"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio data to transcribe
            engine: Transcription engine to use ("google", "sphinx", etc.)
            
        Returns:
            Dictionary with transcription results
        """
        if not _audio_available or not self.recognizer:
            return {"success": False, "error": "Audio transcription not available"}
        
        try:
            text = ""
            
            if engine == "google":
                text = self.recognizer.recognize_google(audio_data)
            elif engine == "sphinx":
                text = self.recognizer.recognize_sphinx(audio_data)
            else:
                return {
                    "success": False, 
                    "error": f"Unknown transcription engine: {engine}"
                }
            
            return {
                "success": True,
                "text": text,
                "engine": engine
            }
        
        except sr.UnknownValueError:
            return {
                "success": False,
                "error": "Could not understand audio"
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "error": f"Error with recognition service: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Transcription error: {e}"
            }
    
    def process_and_transcribe(
        self, 
        duration: int = 5, 
        engine: str = "google", 
        denoise: bool = True
    ) -> Dict[str, Any]:
        """
        Record, process, and transcribe audio in one step
        
        Args:
            duration: Recording duration in seconds
            engine: Transcription engine to use
            denoise: Whether to denoise the audio
            
        Returns:
            Dictionary with transcription results
        """
        if not _audio_available or not self.recognizer:
            return {"success": False, "error": "Audio processing not available"}
        
        # Record audio
        audio_data = self.record_audio(duration)
        if not audio_data:
            return {"success": False, "error": "Failed to record audio"}
        
        # Denoise if requested
        if denoise:
            processed_audio = self.denoise_audio(audio_data)
            if processed_audio:
                audio_data = processed_audio
        
        # Transcribe
        return self.transcribe_audio(audio_data, engine)

# Create singleton instance
_preprocessor = AudioPreprocessor()

def record_and_transcribe(
    duration: int = 5, 
    engine: str = "google", 
    denoise: bool = True
) -> Dict[str, Any]:
    """
    Record and transcribe audio
    
    Args:
        duration: Recording duration in seconds
        engine: Transcription engine to use
        denoise: Whether to denoise the audio
        
    Returns:
        Transcription results
    """
    return _preprocessor.process_and_transcribe(duration, engine, denoise)

def check_audio_availability() -> bool:
    """
    Check if audio functionality is available
    
    Returns:
        True if audio is available, False otherwise
    """
    return _audio_available


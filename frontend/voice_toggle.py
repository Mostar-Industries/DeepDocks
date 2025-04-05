import streamlit as st
import sys
import os

# Add the parent directory to sys.path to enable imports from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import voice module
from backend.voice.speak import speak_text, check_voice_availability

def voice_toggle_component():
    """
    Creates a voice toggle component that can be embedded in other Streamlit pages
    Returns the current state of the voice toggle
    """
    
    # Check if voice system is available
    voice_available = check_voice_availability()
    
    if not voice_available:
        st.warning("Voice system is not available on this device. Please check your audio configuration.")
        return False
    
    # Create the toggle
    voice_enabled = st.toggle("Enable Voice Feedback", value=False)
    
    # Add voice settings if enabled
    if voice_enabled:
        st.subheader("Voice Settings")
        
        voice_type = st.selectbox(
            "Voice Type",
            options=["Default", "Male", "Female"],
            index=0
        )
        
        voice_speed = st.slider(
            "Voice Speed", 
            min_value=0.5, 
            max_value=2.0, 
            value=1.0, 
            step=0.1
        )
        
        # Voice test button
        if st.button("Test Voice"):
            test_message = "This is a test of the DeepCAL++ voice system. Voice feedback is now enabled."
            speak_text(test_message, voice_type=voice_type.lower(), speed=voice_speed)
            st.success("Voice test complete!")
    
    return voice_enabled


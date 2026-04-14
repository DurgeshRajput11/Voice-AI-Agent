"""
Audio Utility Module
Handles audio recording and file operations
"""
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import Optional
import tempfile

class AudioRecorder:
    """Audio recording and management"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = None
    
    def record(self, duration: int = 10) -> np.ndarray:
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Audio data as numpy array
        """
        print(f"Recording for {duration} seconds...")
        
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32'
        )
        
        sd.wait()  
        
        print("Recording complete!")
        return recording
    
    def save_audio(self, audio_data: np.ndarray, output_path: Path) -> Path:
        """
        Save audio data to file
        
        Args:
            audio_data: Audio data as numpy array
            output_path: Path to save audio file
            
        Returns:
            Path to saved file
        """
        sf.write(str(output_path), audio_data, self.sample_rate)
        return output_path
    
    def create_temp_audio_file(self, audio_data: np.ndarray) -> Path:
        """
        Create temporary audio file
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Path to temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_path = Path(temp_file.name)
        temp_file.close()
        
        return self.save_audio(audio_data, temp_path)
    
    @staticmethod
    def get_audio_info(audio_path: Path) -> dict:
        """Get audio file information"""
        try:
            info = sf.info(str(audio_path))
            return {
                "duration": info.duration,
                "sample_rate": info.samplerate,
                "channels": info.channels,
                "format": info.format,
                "subtype": info.subtype
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def convert_to_wav(input_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Convert audio file to WAV format
        
        Args:
            input_path: Path to input audio file
            output_path: Optional output path (creates temp if not provided)
            
        Returns:
            Path to WAV file
        """
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(str(input_path))
            
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                output_path = Path(temp_file.name)
                temp_file.close()
            
            audio.export(str(output_path), format='wav')
            return output_path
            
        except Exception as e:
            print(f"Conversion error: {e}")
           
            if str(input_path).lower().endswith('.wav'):
                return input_path
            raise
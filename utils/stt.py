"""
Speech-to-Text Module
Handles audio transcription using local HuggingFace models or API fallback
"""
import os
import torch
from typing import Optional, Dict
import warnings
warnings.filterwarnings("ignore")

class STTProcessor:
    """Speech-to-Text Processor with local and API support"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.use_local = config.get("use_local", True)
        self.device = config.get("device", "cpu")
        self.model = None
        self.processor = None
        
        if self.use_local:
            self._initialize_local_model()
    
    def _initialize_local_model(self):
        """Initialize local Whisper model from HuggingFace"""
        try:
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
            
            model_id = self.config.get("local_model", "openai/whisper-base")
            
            print(f"Loading {model_id} on {self.device}...")
            
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True
            )
            model.to(self.device)
            
            processor = AutoProcessor.from_pretrained(model_id)
            
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
                max_new_tokens=128,
                chunk_length_s=30,
                batch_size=16,
                return_timestamps=False,
                torch_dtype=torch_dtype,
                device=self.device,
            )
            
            print("✓ Local STT model loaded successfully")
            
        except Exception as e:
            print(f"✗ Failed to load local model: {e}")
            print("Switching to API fallback...")
            self.use_local = False
    
    def transcribe(self, audio_path: str) -> Dict[str, str]:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with transcription and metadata
        """
        try:
            if self.use_local:
                return self._transcribe_local(audio_path)
            else:
                return self._transcribe_api(audio_path)
        except Exception as e:
            return {
                "text": "",
                "error": str(e),
                "success": False
            }
    
    def _transcribe_local(self, audio_path: str) -> Dict[str, str]:
        """Transcribe using local Whisper model"""
        try:
            result = self.pipe(audio_path)
            return {
                "text": result["text"].strip(),
                "method": "local",
                "model": self.config.get("local_model"),
                "success": True
            }
        except Exception as e:
            raise Exception(f"Local transcription failed: {e}")
    
    def _transcribe_api(self, audio_path: str) -> Dict[str, str]:
        """Transcribe using API (Groq or OpenAI)"""
        api_provider = self.config.get("api_provider", "groq")
        
        try:
            if api_provider == "groq":
                return self._transcribe_groq(audio_path)
            elif api_provider == "openai":
                return self._transcribe_openai(audio_path)
            else:
                raise ValueError(f"Unknown API provider: {api_provider}")
        except Exception as e:
            raise Exception(f"API transcription failed: {e}")
    
    def _transcribe_groq(self, audio_path: str) -> Dict[str, str]:
        """Transcribe using Groq API"""
        try:
            from groq import Groq
            
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment")
            
            client = Groq(api_key=api_key)
            
            with open(audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="text"
                )
            
            return {
                "text": transcription.strip(),
                "method": "groq_api",
                "model": "whisper-large-v3",
                "success": True
            }
        except Exception as e:
            raise Exception(f"Groq API error: {e}")
    
    def _transcribe_openai(self, audio_path: str) -> Dict[str, str]:
        """Transcribe using OpenAI API"""
        try:
            from openai import OpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            
            client = OpenAI(api_key=api_key)
            
            with open(audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            return {
                "text": transcription.text.strip(),
                "method": "openai_api",
                "model": "whisper-1",
                "success": True
            }
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
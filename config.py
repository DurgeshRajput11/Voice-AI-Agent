"""
Configuration file for Voice AI Agent
"""
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
AUDIO_SAMPLES_DIR = PROJECT_ROOT / "audio_samples"


OUTPUT_DIR.mkdir(exist_ok=True)
AUDIO_SAMPLES_DIR.mkdir(exist_ok=True)


STT_CONFIG = {
    "local_model": "openai/whisper-base",  
    "use_local": True,  
    "api_provider": "groq",  
    "device": "cpu", 
}


LLM_CONFIG = {
    "provider": "ollama",  
    "model": "llama3.2:3b", 
    "base_url": "http://localhost:11434",
    "temperature": 0.7,
    "max_tokens": 2000,
}


SUPPORTED_INTENTS = [
    "create_file",
    "write_code",
    "summarize_text",
    "general_chat",
]


INTENT_CLASSIFICATION_PROMPT = """You are an intent classification system. Analyze the user's request and classify it into ONE of these categories:

1. create_file - User wants to create a file or folder
2. write_code - User wants to generate code and save it to a file
3. summarize_text - User wants to summarize text content
4. general_chat - General conversation or questions

User request: {user_input}

Respond ONLY with a JSON object in this exact format:
{{
    "intent": "one_of_the_intents_above",
    "confidence": 0.95,
    "parameters": {{
        "filename": "extracted_filename_if_mentioned",
        "language": "programming_language_if_code",
        "content": "text_to_summarize_or_file_content"
    }}
}}"""

CODE_GENERATION_PROMPT = """You are a code generation assistant. Generate clean, well-commented code based on the user's request.

User request: {user_input}
Programming language: {language}

Generate ONLY the code without any explanations or markdown formatting. The code will be saved directly to a file."""

SUMMARIZATION_PROMPT = """Summarize the following text concisely:

{text}

Provide a clear, brief summary highlighting the key points."""


AUDIO_CONFIG = {
    "sample_rate": 16000,
    "channels": 1,
    "duration": 10,  
}


UI_CONFIG = {
    "title": "🎤 Voice-Controlled AI Agent",
    "theme": "dark",
    "max_history": 10,
}
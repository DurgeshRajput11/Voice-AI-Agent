"""
LLM Module
Handles intent classification and AI-powered tasks using local or API models
"""
import json
import os
from typing import Dict, Optional
import requests

class LLMProcessor:
    """LLM Processor for intent classification and task execution"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.provider = config.get("provider", "ollama")
        self.model = config.get("model", "llama3.2:3b")
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2000)
        
       
        if self.provider == "ollama":
            self._test_ollama_connection()
    
    def _test_ollama_connection(self):
        """Test if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                if self.model in model_names:
                    print(f"✓ Connected to Ollama - Model '{self.model}' is available")
                else:
                    print(f"⚠ Warning: Model '{self.model}' not found. Available models: {model_names}")
                    print(f"  Run: ollama pull {self.model}")
            else:
                print(f"✗ Ollama connection failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Cannot connect to Ollama: {e}")
            print(f"  Make sure Ollama is running: ollama serve")
    
    def classify_intent(self, user_input: str, prompt_template: str) -> Dict:
        """
        Classify user intent from transcribed text
        
        Args:
            user_input: Transcribed user request
            prompt_template: Template for intent classification
            
        Returns:
            Dictionary with intent, confidence, and parameters
        """
        prompt = prompt_template.format(user_input=user_input)
        
        try:
            response = self._call_llm(prompt)
            

            response_text = response.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            
          
            if "intent" not in result:
                raise ValueError("No intent field in response")
            
            return {
                "intent": result.get("intent", "general_chat"),
                "confidence": result.get("confidence", 0.5),
                "parameters": result.get("parameters", {}),
                "success": True
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Raw response: {response}")
            return {
                "intent": "general_chat",
                "confidence": 0.3,
                "parameters": {},
                "success": False,
                "error": f"Failed to parse intent: {str(e)}"
            }
        except Exception as e:
            print(f"Intent classification error: {e}")
            return {
                "intent": "general_chat",
                "confidence": 0.0,
                "parameters": {},
                "success": False,
                "error": str(e)
            }
    
    def generate_code(self, user_input: str, language: str, prompt_template: str) -> str:
        """Generate code based on user request"""
        prompt = prompt_template.format(user_input=user_input, language=language)
        
        try:
            code = self._call_llm(prompt)
            
            code = code.strip()
            if code.startswith("```"):
                lines = code.split("\n")
                code = "\n".join(lines[1:-1]) if len(lines) > 2 else code
            return code
        except Exception as e:
            return f"# Error generating code: {e}"
    
    def summarize_text(self, text: str, prompt_template: str) -> str:
        """Summarize provided text"""
        prompt = prompt_template.format(text=text)
        
        try:
            summary = self._call_llm(prompt)
            return summary.strip()
        except Exception as e:
            return f"Error summarizing text: {e}"
    
    def chat(self, user_input: str) -> str:
        """General chat response"""
        try:
            response = self._call_llm(user_input)
            return response.strip()
        except Exception as e:
            return f"Error: {e}"
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM based on configured provider"""
        if self.provider == "ollama":
            return self._call_ollama(prompt)
        elif self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "groq":
            return self._call_groq(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Ollama call failed: {e}")
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            from openai import OpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")
            
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"OpenAI call failed: {e}")
    
    def _call_groq(self, prompt: str) -> str:
        """Call Groq API"""
        try:
            from groq import Groq
            
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found")
            
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Groq call failed: {e}")
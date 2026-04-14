"""
Main Voice AI Agent Application
Orchestrates STT, LLM, and Tool Execution
"""
from pathlib import Path
from typing import Dict, Optional
import json
from datetime import datetime

from utils import STTProcessor, LLMProcessor, ToolExecutor, AudioRecorder
import config

class VoiceAIAgent:
    """Main Voice AI Agent orchestrator"""
    
    def __init__(self):
        """Initialize all components"""
        print("Initializing Voice AI Agent...")
        
      
        self.stt = STTProcessor(config.STT_CONFIG)
        self.llm = LLMProcessor(config.LLM_CONFIG)
        self.tools = ToolExecutor(config.OUTPUT_DIR, self.llm)
        self.audio_recorder = AudioRecorder(
            sample_rate=config.AUDIO_CONFIG["sample_rate"],
            channels=config.AUDIO_CONFIG["channels"]
        )
        
       
        self.session_history = []
        
        print("✓ Voice AI Agent initialized successfully!")
    
    def process_audio_file(self, audio_path: str) -> Dict:
        """
        Process uploaded audio file through the complete pipeline
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Complete execution result
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "audio_path": audio_path,
            "transcription": None,
            "intent": None,
            "execution": None,
            "success": False
        }
        
        try:
       
            print("\n[1/4] Transcribing audio...")
            transcription = self.stt.transcribe(audio_path)
            
            if not transcription.get("success"):
                result["error"] = transcription.get("error", "Transcription failed")
                return result
            
            result["transcription"] = transcription
            transcribed_text = transcription["text"]
            
            if not transcribed_text:
                result["error"] = "No speech detected in audio"
                return result
            
            print(f"✓ Transcription: {transcribed_text}")
            
          
            print("\n[2/4] Classifying intent...")
            intent_result = self.llm.classify_intent(
                transcribed_text,
                config.INTENT_CLASSIFICATION_PROMPT
            )
            
            result["intent"] = intent_result
            intent = intent_result.get("intent", "general_chat")
            confidence = intent_result.get("confidence", 0.0)
            parameters = intent_result.get("parameters", {})
            
            print(f"✓ Intent: {intent} (confidence: {confidence:.2f})")
            
            print(f"\n[3/4] Executing action: {intent}...")
            
            prompts = {
                "code_generation": config.CODE_GENERATION_PROMPT,
                "summarization": config.SUMMARIZATION_PROMPT
            }
            
            execution_result = self.tools.execute(
                intent=intent,
                parameters=parameters,
                user_input=transcribed_text,
                prompts=prompts
            )
            
            result["execution"] = execution_result
            
            if execution_result.get("success"):
                print(f"✓ Action completed: {execution_result.get('action')}")
                result["success"] = True
            else:
                print(f"✗ Action failed: {execution_result.get('error')}")
                result["error"] = execution_result.get("error")
            
          
            self.session_history.append(result)
            
            return result
            
        except Exception as e:
            result["error"] = f"Pipeline error: {str(e)}"
            print(f"✗ Error: {e}")
            return result
    
    def process_microphone_recording(self, duration: int = 10) -> Dict:
        """
        Record from microphone and process through pipeline
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Complete execution result
        """
        try:
          
            print(f"\n🎤 Recording for {duration} seconds...")
            audio_data = self.audio_recorder.record(duration)
            
          
            temp_path = self.audio_recorder.create_temp_audio_file(audio_data)
            
           
            result = self.process_audio_file(str(temp_path))
            result["recording_duration"] = duration
            
            return result
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": f"Recording error: {str(e)}",
                "success": False
            }
    
    def get_session_history(self) -> list:
        """Get session history"""
        return self.session_history
    
    def clear_session(self):
        """Clear session history"""
        self.session_history = []
        self.tools.clear_history()
    
    def export_session(self, output_path: Optional[Path] = None) -> Path:
        """Export session history to JSON"""
        if output_path is None:
            output_path = config.OUTPUT_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.session_history, f, indent=2, default=str)
        
        return output_path
    
    def get_stats(self) -> Dict:
        """Get session statistics"""
        if not self.session_history:
            return {
                "total_requests": 0,
                "successful": 0,
                "failed": 0,
                "intents": {}
            }
        
        stats = {
            "total_requests": len(self.session_history),
            "successful": sum(1 for r in self.session_history if r.get("success")),
            "failed": sum(1 for r in self.session_history if not r.get("success")),
            "intents": {}
        }
        
    
        for result in self.session_history:
            if result.get("intent"):
                intent = result["intent"].get("intent", "unknown")
                stats["intents"][intent] = stats["intents"].get(intent, 0) + 1
        
        return stats


if __name__ == "__main__":
  
    agent = VoiceAIAgent()
    
    print("\n" + "="*60)
    print("Voice AI Agent Test")
    print("="*60)
    
    
    test_input = "Create a Python file called hello.py with a simple hello world function"
    print(f"\nTest input: {test_input}")
    
    
    print("\nAgent initialized and ready!")
    print("\nTo use the agent, run: streamlit run app.py")
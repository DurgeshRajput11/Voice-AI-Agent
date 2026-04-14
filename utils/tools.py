"""
Tool Executor Module
Executes actions based on classified intent (file creation, code generation, etc.)
"""
import os
from pathlib import Path
from typing import Dict, Optional
import json
from datetime import datetime

class ToolExecutor:
    """Executes tools and actions based on intent"""
    
    def __init__(self, output_dir: Path, llm_processor):
        self.output_dir = output_dir
        self.llm = llm_processor
        self.execution_history = []
    
    def execute(self, intent: str, parameters: Dict, user_input: str, prompts: Dict) -> Dict:
        """
        Execute action based on intent
        
        Args:
            intent: Classified intent
            parameters: Extracted parameters from intent classification
            user_input: Original user input
            prompts: Dictionary of prompt templates
            
        Returns:
            Execution result dictionary
        """
        try:
            if intent == "create_file":
                return self._create_file(parameters, user_input)
            elif intent == "write_code":
                return self._write_code(parameters, user_input, prompts.get("code_generation"))
            elif intent == "summarize_text":
                return self._summarize_text(parameters, user_input, prompts.get("summarization"))
            elif intent == "general_chat":
                return self._general_chat(user_input)
            else:
                return {
                    "success": False,
                    "error": f"Unknown intent: {intent}",
                    "action": "error"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "error"
            }
    
    def _create_file(self, parameters: Dict, user_input: str) -> Dict:
        """Create a file or folder"""
        try:
            filename = parameters.get("filename")
            content = parameters.get("content", "")
            
            if not filename:
                filename = self._extract_filename(user_input)
            
            if not filename:
                filename = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            safe_filename = self._sanitize_filename(filename)
            file_path = self.output_dir / safe_filename
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content if content else f"# File created by Voice AI Agent\n# Created: {datetime.now()}\n")
            
            result = {
                "success": True,
                "action": "created_file",
                "file_path": str(file_path.relative_to(self.output_dir.parent)),
                "filename": safe_filename,
                "output": f"Successfully created file: {safe_filename}"
            }
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create file: {e}",
                "action": "error"
            }
    
    def _write_code(self, parameters: Dict, user_input: str, code_prompt: str) -> Dict:
        """Generate and save code to a file"""
        try:
            
            language = parameters.get("language", "python")
            filename = parameters.get("filename")
            
            if not filename:
                filename = self._extract_filename(user_input)
            
           
            extensions = {
                "python": ".py",
                "javascript": ".js",
                "java": ".java",
                "cpp": ".cpp",
                "c": ".c",
                "html": ".html",
                "css": ".css",
                "typescript": ".ts",
                "go": ".go",
                "rust": ".rs"
            }
            
            ext = extensions.get(language.lower(), ".txt")
            
            if not filename:
                filename = f"code_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            elif not any(filename.endswith(e) for e in extensions.values()):
                filename += ext
            
            print(f"Generating {language} code...")
            code = self.llm.generate_code(user_input, language, code_prompt)
            
            safe_filename = self._sanitize_filename(filename)
            file_path = self.output_dir / safe_filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            result = {
                "success": True,
                "action": "wrote_code",
                "file_path": str(file_path.relative_to(self.output_dir.parent)),
                "filename": safe_filename,
                "language": language,
                "code": code,
                "output": f"Successfully generated {language} code and saved to: {safe_filename}"
            }
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to write code: {e}",
                "action": "error"
            }
    
    def _summarize_text(self, parameters: Dict, user_input: str, summarization_prompt: str) -> Dict:
        """Summarize text content"""
        try:
           
            text = parameters.get("content", "")
            
            if not text:
               
                text = user_input
            
            if len(text) < 50:
                return {
                    "success": False,
                    "error": "Text too short to summarize. Please provide more content.",
                    "action": "error"
                }
            
            print("Generating summary...")
            summary = self.llm.summarize_text(text, summarization_prompt)
            
          
            filename = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            file_path = self.output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Original Text:\n{'-'*50}\n{text}\n\n")
                f.write(f"Summary:\n{'-'*50}\n{summary}\n")
            
            result = {
                "success": True,
                "action": "summarized_text",
                "file_path": str(file_path.relative_to(self.output_dir.parent)),
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary),
                "output": summary
            }
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to summarize text: {e}",
                "action": "error"
            }
    
    def _general_chat(self, user_input: str) -> Dict:
        """Handle general chat"""
        try:
            print("Processing chat request...")
            response = self.llm.chat(user_input)
            
            result = {
                "success": True,
                "action": "chat_response",
                "output": response
            }
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Chat failed: {e}",
                "action": "error"
            }
    
    def _extract_filename(self, text: str) -> Optional[str]:
        """Extract potential filename from text"""
        import re
        
        patterns = [
            r'(?:file|called|named)\s+["\']?([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)["\']?',
            r'["\']([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)["\']',
            r'(?:to|into|in)\s+([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        
        filename = os.path.basename(filename)
        
        filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        
        if not filename:
            filename = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        return filename
    
    def get_history(self) -> list:
        """Get execution history"""
        return self.execution_history
    
    def clear_history(self):
        """Clear execution history"""
        self.execution_history = []
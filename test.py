"""
Voice AI Agent - System Test
Tests all components to verify installation
"""
import sys
from pathlib import Path

def test_imports():
    """Test if all required packages are installed"""
    print("🧪 Testing package imports...")
    
    required_packages = [
        ('streamlit', 'Streamlit UI'),
        ('sounddevice', 'Audio recording'),
        ('soundfile', 'Audio file handling'),
        ('transformers', 'HuggingFace models'),
        ('torch', 'PyTorch'),
        ('requests', 'HTTP requests'),
    ]
    
    failed = []
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {description} ({package})")
        except ImportError:
            print(f"  ✗ {description} ({package}) - NOT INSTALLED")
            failed.append(package)
    
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All packages installed\n")
    return True

def test_config():
    """Test if config is accessible"""
    print("🧪 Testing configuration...")
    
    try:
        import config
        print(f"  ✓ Config loaded")
        print(f"  ✓ Output dir: {config.OUTPUT_DIR}")
        print(f"  ✓ STT model: {config.STT_CONFIG.get('local_model')}")
        print(f"  ✓ LLM model: {config.LLM_CONFIG.get('model')}")
        print("✅ Configuration OK\n")
        return True
    except Exception as e:
        print(f"  ✗ Config error: {e}")
        return False

def test_utils():
    """Test if utility modules load"""
    print("🧪 Testing utility modules...")
    
    try:
        from utils import STTProcessor, LLMProcessor, ToolExecutor, AudioRecorder
        print("  ✓ All utility modules loaded")
        print("✅ Utilities OK\n")
        return True
    except Exception as e:
        print(f"  ✗ Utilities error: {e}")
        return False

def test_ollama():
    """Test Ollama connection"""
    print("🧪 Testing Ollama connection...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"  ✓ Ollama is running")
            print(f"  ✓ Available models: {len(models)}")
            
            model_names = [m.get("name") for m in models]
            if "llama3.2:3b" in model_names:
                print(f"  ✓ llama3.2:3b model is available")
            else:
                print(f"  ⚠ llama3.2:3b not found. Run: ollama pull llama3.2:3b")
            
            print("✅ Ollama OK\n")
            return True
        else:
            print(f"  ✗ Ollama returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ✗ Cannot connect to Ollama: {e}")
        print("  Make sure Ollama is running: ollama serve")
        return False

def test_directories():
    """Test if required directories exist"""
    print("🧪 Testing directory structure...")
    
    import config
    dirs = [config.OUTPUT_DIR, config.AUDIO_SAMPLES_DIR]
    
    for dir_path in dirs:
        if dir_path.exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} - NOT FOUND")
            return False
    
    print("✅ Directories OK\n")
    return True

def test_agent_init():
    """Test agent initialization"""
    print("🧪 Testing agent initialization...")
    
    try:
        from agent import VoiceAIAgent
        
       
        print("  Loading agent (this may take a moment)...")
        agent = VoiceAIAgent()
        
        print("  ✓ Agent initialized successfully")
        print("✅ Agent OK\n")
        return True
        
    except Exception as e:
        print(f"  ✗ Agent initialization failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Voice AI Agent - System Test")
    print("="*60 + "\n")
    
    tests = [
        ("Package Imports", test_imports),
        ("Configuration", test_config),
        ("Utility Modules", test_utils),
        ("Directory Structure", test_directories),
        ("Ollama Connection", test_ollama),
        ("Agent Initialization", test_agent_init),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} crashed: {e}\n")
            results.append((name, False))
    
    print("="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your system is ready.")
        print("\nTo start the application:")
        print("  streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
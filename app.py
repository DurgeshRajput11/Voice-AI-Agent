"""
Voice AI Agent - Streamlit UI
Interactive web interface for the Voice AI Agent
"""
import streamlit as st
from pathlib import Path
import os
import tempfile
from datetime import datetime
import json


from agent import VoiceAIAgent
import config


st.set_page_config(
    page_title="Voice AI Agent",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .step-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

if 'agent' not in st.session_state:
    with st.spinner(" Initializing Voice AI Agent..."):
        st.session_state.agent = VoiceAIAgent()
        st.session_state.initialized = True

if 'results_history' not in st.session_state:
    st.session_state.results_history = []


st.markdown('<h1 class="main-header">🎤 Voice-Controlled AI Agent</h1>', unsafe_allow_html=True)
st.markdown("---")


with st.sidebar:
    st.header("⚙️ Configuration")
    
   
    st.subheader(" Models")
    st.info(f"""
    **STT Model:** {config.STT_CONFIG.get('local_model', 'API')}  
    **LLM Model:** {config.LLM_CONFIG.get('model', 'N/A')}  
    **Device:** {config.STT_CONFIG.get('device', 'cpu')}
    """)
    
    st.subheader(" Supported Intents")
    for intent in config.SUPPORTED_INTENTS:
        st.write(f"• {intent.replace('_', ' ').title()}")
    
    st.markdown("---")
    
    st.subheader(" Session")
    
    if st.button("🗑️ Clear History"):
        st.session_state.agent.clear_session()
        st.session_state.results_history = []
        st.success("History cleared!")
        st.rerun()
    
    if st.button(" Export Session"):
        export_path = st.session_state.agent.export_session()
        st.success(f"Session exported to:\n`{export_path}`")
    
    
    stats = st.session_state.agent.get_stats()
    if stats["total_requests"] > 0:
        st.metric("Total Requests", stats["total_requests"])
        st.metric("Success Rate", f"{stats['successful']/stats['total_requests']*100:.1f}%")


tab1, tab2, tab3 = st.tabs(["🎙️ Voice Input", "📁 Upload Audio", "📜 History"])


with tab1:
    st.header("Record from Microphone")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        duration = st.slider(
            "Recording Duration (seconds)",
            min_value=3,
            max_value=30,
            value=10,
            help="How long to record audio"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🎤 Start Recording", type="primary", use_container_width=True):
            try:
                with st.spinner(f"🎤 Recording for {duration} seconds..."):
                    result = st.session_state.agent.process_microphone_recording(duration)
                    st.session_state.results_history.append(result)
                    st.rerun()
            except Exception as e:
                st.error(f"Recording error: {e}")
    
    st.info(" **Tip:** Click the button and speak clearly. The agent will transcribe, classify intent, and execute the action automatically!")

with tab2:
    st.header("Upload Audio File")
    
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'ogg', 'm4a', 'flac'],
        help="Upload an audio file to process"
    )
    
    if uploaded_file is not None:
      
        st.write(f"**Filename:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size / 1024:.2f} KB")
        
     
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
    
        st.audio(uploaded_file, format=f'audio/{Path(uploaded_file.name).suffix[1:]}')
        
        if st.button(" Process Audio", type="primary"):
            with st.spinner("Processing audio..."):
                result = st.session_state.agent.process_audio_file(temp_path)
                st.session_state.results_history.append(result)
                st.rerun()


with tab3:
    st.header("Execution History")
    
    if not st.session_state.results_history:
        st.info("No executions yet. Process some audio to see results here!")
    else:
      
        for idx, result in enumerate(reversed(st.session_state.results_history)):
            with st.expander(
                f"{'✅' if result.get('success') else '❌'} Request {len(st.session_state.results_history) - idx} - {result.get('timestamp', 'N/A')[:19]}",
                expanded=(idx == 0)
            ):
              
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("###  Transcription")
                    if result.get('transcription'):
                        st.success(result['transcription'].get('text', 'N/A'))
                        st.caption(f"Method: {result['transcription'].get('method', 'N/A')}")
                    else:
                        st.error("Transcription failed")
                
                with col2:
                    st.markdown("###  Intent")
                    if result.get('intent'):
                        intent = result['intent'].get('intent', 'N/A')
                        confidence = result['intent'].get('confidence', 0)
                        st.info(f"**{intent.replace('_', ' ').title()}**")
                        st.caption(f"Confidence: {confidence:.2%}")
                    else:
                        st.error("Intent classification failed")
                
                with col3:
                    st.markdown("###  Execution")
                    if result.get('execution'):
                        exec_result = result['execution']
                        if exec_result.get('success'):
                            st.success(exec_result.get('action', 'N/A').replace('_', ' ').title())
                            if 'file_path' in exec_result:
                                st.caption(f" {exec_result['file_path']}")
                        else:
                            st.error(f"Failed: {exec_result.get('error', 'Unknown error')}")
                    else:
                        st.error("Execution failed")
                
                if result.get('execution') and result['execution'].get('success'):
                    st.markdown("---")
                    st.markdown("###  Output")
                    
                    exec_result = result['execution']
                    
                 
                    if 'code' in exec_result:
                        st.code(exec_result['code'], language=exec_result.get('language', 'python'))
                    
                   
                    if 'summary' in exec_result:
                        st.markdown(exec_result['summary'])
                    
                    
                    if 'output' in exec_result:
                        st.write(exec_result['output'])

if st.session_state.results_history:
    st.markdown("---")
    st.header(" Latest Result")
    
    latest = st.session_state.results_history[-1]
    
    if latest.get('success'):
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("###  Success!")
        
    
        if latest.get('transcription'):
            st.markdown(f"**You said:** {latest['transcription'].get('text', 'N/A')}")
        
        if latest.get('intent'):
            intent = latest['intent'].get('intent', 'N/A').replace('_', ' ').title()
            st.markdown(f"**Detected Intent:** {intent}")
        
        if latest.get('execution'):
            exec_result = latest['execution']
            st.markdown(f"**Action:** {exec_result.get('action', 'N/A').replace('_', ' ').title()}")
            
            if 'output' in exec_result:
                st.markdown(f"**Result:** {exec_result['output']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.markdown("### ❌ Error")
        st.markdown(f"**Error:** {latest.get('error', 'Unknown error')}")
        st.markdown('</div>', unsafe_allow_html=True)


st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Voice-Controlled AI Agent </p>
    <p>Powered by Local AI Models</p>
</div>
""", unsafe_allow_html=True)
import streamlit as st
import os
from dotenv import load_dotenv
import reflection_logic

# Load environment variables
from openai import OpenAI
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
import io
import time
import random

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config (Must be first Streamlit command)
st.set_page_config(
    page_title="Ura Warriors - Reflection Session",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Helper Functions ---

def transcribe_audio(audio_bytes):
    """Convert audio bytes to text using OpenAI Whisper (handles webm/wav/etc)."""
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "input.webm"
        
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcript.text
    except Exception as e:
        st.error(f"Error processing audio: {e}")
        return None

def generate_ai_response_audio(text, voice_selection):
    """Generate audio from text using OpenAI TTS."""
    voice_map = {
        "Calm Female": "nova",
        "Calm Male": "onyx",
        "Neutral AI": "alloy",
        "Friendly AI": "shimmer"
    }
    voice_id = voice_map.get(voice_selection, "alloy")
    
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice_id,
            input=text
        )
        return io.BytesIO(response.content)
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None

def process_interaction(user_text):
    """Main logic: Summary -> Logic -> Response -> Cleanup."""
    
    st.session_state.messages.append({"role": "user", "content": user_text})
    
    if st.session_state.current_state == "Intro":
        next_q = reflection_logic.REFLECTION_DATASET[0]["text"]
        next_step = {
            "next_question": next_q, 
            "response_style": "Briefly acknowledge enthusiasm or readiness.",
            "should_close": False
        }
    else:
        next_step = reflection_logic.get_next_action(
            st.session_state.current_state,
            st.session_state.question_count
        )
    
    context_messages = [
        {"role": "system", "content": f"You are a Ura-warrior. A wise, reflective AI. Guidelines: {next_step['response_style']}"}
    ]
    history = st.session_state.messages[-4:] 
    for msg in history:
        context_messages.append({"role": msg["role"], "content": msg["content"]})
    
    prompt = f"User said: '{user_text}'. Validate their feeling briefly, then ask: '{next_step['next_question']}'"
    if next_step['should_close']:
         prompt = (
             f"User said: '{user_text}'. This is the final response. "
             "Reflect on the user's answers throughout the session (available in context). "
             "Provide a gentle, supportive closing summary and one piece of safe, non-clinical advice. "
             "IMPORTANT: End with a mandatory disclaimer that you are an AI and this is not professional therapy."
         )

    context_messages.append({"role": "user", "content": prompt})

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=context_messages,
            max_tokens=150
        )
        ai_text = completion.choices[0].message.content
    except Exception as e:
        ai_text = "I'm having trouble connecting. Let's pause."
        st.error(f"LLM Error: {e}")

    st.session_state.messages.append({"role": "assistant", "content": ai_text})
    
    if next_step['should_close']:
        st.session_state.current_state = "Close"
        return ai_text, True  # Return tuple with closing flag
    else:
        st.session_state.question_count += 1
        if st.session_state.current_state == "Intro":
             st.session_state.current_state = "Q1"
        else:
             st.session_state.current_state = f"Q{st.session_state.question_count + 1}"

    return ai_text, False  # Not closing


# POLISHED CSS - Clean and bug-free
st.markdown("""
<style>
    /* Import beautiful fonts */
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@300;400;600&family=DM+Sans:wght@400;500;700&family=Playfair+Display:wght@600;700&display=swap');
    
    /* Beautiful therapeutic background */
    .stApp {
        background: linear-gradient(135deg, 
            #f8f4f0 0%, 
            #e8ded2 25%,
            #dcd0c0 50%,
            #f0e6d8 75%,
            #f8f4f0 100%
        );
        background-attachment: fixed;
    }
    
    /* Container spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 800px !important;
    }
    
    /* Remove extra padding/margins from Streamlit elements */
    .element-container {
        margin-bottom: 0 !important;
    }
    
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] {
        gap: 0 !important;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #5a4a3a !important;
    }
    
    .stApp, p, label {
        font-family: 'DM Sans', sans-serif !important;
        color: #5a4a3a !important;
    }
    
    /* Radio buttons - Beautiful cards */
    .stRadio > div {
        gap: 0.8rem;
        display: flex;
        flex-direction: column;
    }
    
    .stRadio > div > label {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 244, 240, 0.95) 100%);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        border: 2px solid rgba(166, 142, 108, 0.2);
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'DM Sans', sans-serif;
        font-size: 1rem;
        color: #5a4a3a;
        font-weight: 500;
        display: flex;
        align-items: center;
        margin: 0;
    }
    
    .stRadio > div > label:hover {
        border-color: #a68e6c;
        transform: translateX(6px);
        background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(248, 244, 240, 1) 100%);
        box-shadow: 0 4px 12px rgba(139, 115, 85, 0.15);
    }
    
    /* Selected radio button */
    .stRadio > div > label:has(input:checked) {
        border-color: #8b7355;
        background: linear-gradient(135deg, #f0e6d8 0%, #e8ded2 100%);
        font-weight: 600;
    }
    
    /* target all buttons for consistent premium look including external components */
    button {
        background: linear-gradient(135deg, #8b7355 0%, #a68e6c 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.8rem 2rem !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(139, 115, 85, 0.2) !important;
        transition: all 0.3s ease !important;
        margin: 0 auto !important;
        display: block !important;
        width: auto !important;
        min-width: 200px !important;
    }
    
    button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(139, 115, 85, 0.3) !important;
        background: linear-gradient(135deg, #9a8466 0%, #b59d7d 100%) !important;
    }
    
    button:active {
        transform: translateY(1px) !important;
        box-shadow: 0 2px 8px rgba(139, 115, 85, 0.2) !important;
    }

    /* Target specific mic recorder structure if needed to ensure centering */
    .stButton {
        display: flex;
        justify-content: center;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #8b7355 0%, #a68e6c 100%);
    }
    
    .stProgress > div > div {
        background-color: rgba(139, 115, 85, 0.15);
        height: 8px;
    }
    
    /* Expander for transcript */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 12px;
        font-family: 'DM Sans', sans-serif;
        color: #8b7355;
        font-weight: 500;
        padding: 1rem;
        border: 1px solid rgba(166, 142, 108, 0.2);
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: 'Crimson Pro', serif;
        color: #5a4a3a;
        border: 1px solid rgba(166, 142, 108, 0.15);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Lottie player */
    lottie-player {
        filter: drop-shadow(0 4px 12px rgba(139, 115, 85, 0.15));
        margin: 0 auto;
        display: block;
    }
    
    /* Audio player */
    audio {
        width: 100%;
        border-radius: 12px;
        margin-top: 1rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* CSS Animation for processing state */
    @keyframes pulse-ring {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(139, 115, 85, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 20px rgba(139, 115, 85, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(139, 115, 85, 0); }
    }

    .processing-indicator {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #a68e6c, #8b7355);
        margin: 2rem auto;
        animation: pulse-ring 2s infinite ease-in-out;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
</style>
<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
""", unsafe_allow_html=True)

# Session State Management
def initialize_session_state():
    """Initialize all session state variables with defaults."""
    defaults = {
        "current_state": "Landing",
        "last_response_summary": None,
        "emotional_tone": "neutral",
        "question_count": 0,
        "messages": [],
        "current_voice": "Calm Female",
        "session_active": False,
        "processed_audio_ids": []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_session():
    """Reset session variables to start a fresh reflection session."""
    st.session_state.current_state = "Intro"
    st.session_state.last_response_summary = None
    st.session_state.emotional_tone = "neutral"
    st.session_state.question_count = 0
    st.session_state.processed_audio_ids = []
    st.session_state.messages = []
    
    intro_content = (
        f"Hello, I'm your audio reflection assistant. "
        f"My role is to guide you through a few reflective questions to help you explore your thoughts and feelings. "
        f"I will listen carefully and respond gently. Are you ready to begin?"
    )
    
    st.session_state.messages.append({"role": "assistant", "content": intro_content})
    st.session_state.question_count = 0
    st.session_state.session_active = True
    st.session_state.pending_audio = intro_content

initialize_session_state()

# Header
st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='font-family: Playfair Display, serif; 
        font-size: 2.8rem; color: #5a4a3a; margin-bottom: 0.5rem; letter-spacing: -0.02em;'>
            🌿 Ura Warriors
        </h1>
        <p style='font-family: DM Sans, sans-serif; 
        font-size: 1.1rem; color: #8b7355; margin-bottom: 0; letter-spacing: 0.03em;'>
            Your Safe Space for Reflection & Growth
        </p>
    </div>
""", unsafe_allow_html=True)

# Main Interaction Area
if not st.session_state.session_active:
    # Landing Page
    with st.container():
        st.markdown("<h2 style='text-align: center; color: #5a4a3a; font-family: Playfair Display, serif;'>Welcome to Your Reflection Journey</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #5a4a3a; font-size: 1.1rem; line-height: 1.6;'>Find a quiet, comfortable space where you feel safe to reflect. This guided session will help you explore your thoughts and emotions through gentle, non-judgmental conversation. Choose a voice that resonates with you, and let's begin.</p>", unsafe_allow_html=True)
    
    
    # Voice Selection
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #5a4a3a; font-family: Playfair Display, serif;'>Choose Your Companion Voice</h3>", unsafe_allow_html=True)

    
    voice_options = ["Calm Female", "Calm Male", "Neutral AI", "Friendly AI"]
    selected_voice = st.radio(
        "Select Voice",
        voice_options,
        index=0,
        label_visibility="collapsed"
    )
    st.session_state.current_voice = selected_voice
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Start Button
    if st.button("🌱 Begin Your Session", use_container_width=True):
        reset_session()
        st.rerun()
        
else:
    # Active Session
    # Display current question number (capped at max)
    current_q_display = min(st.session_state.question_count + 1, reflection_logic.SESSION_RULES["max_questions"])
    
    with st.container():
        st.markdown(f"""
            <div style='text-align: center; padding: 1rem; background: rgba(255,255,255,0.6); border-radius: 12px; margin-bottom: 1rem;'>
                <div style='font-size: 1.2rem; font-weight: 600; color: #5a4a3a; margin-bottom: 0.25rem;'>Session in Progress</div>
                <div style='color: #8b7355; font-size: 0.9rem;'>Voice: {st.session_state.current_voice}</div>
            </div>
        """, unsafe_allow_html=True)

    
    # Progress Indicator - Only show if not closing
    if st.session_state.current_state != "Close":
        progress = st.session_state.question_count / reflection_logic.SESSION_RULES["max_questions"]
        st.progress(progress, text=f"Question {current_q_display} of {reflection_logic.SESSION_RULES['max_questions']}")
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Animation Area
    with st.container():
        anim_placeholder = st.empty()
    
    # Default Listening State
    with anim_placeholder:
        st.markdown("""
            <div style='display: flex; flex-direction: column; align-items: center; 
            justify-content: center; padding: 2rem 0; min-height: 280px;'>
                <lottie-player 
                    src="https://lottie.host/5a8e1006-2531-40be-bd64-320cce93478d/q5x8zZ7T3g.json" 
                    background="transparent" 
                    speed="1" 
                    style="width: 200px; height: 200px;" 
                    loop 
                    autoplay>
                </lottie-player>
                <div style='font-family: DM Sans, sans-serif; font-size: 1.1rem; 
                color: #8b7355; font-weight: 500; margin-top: 1rem;'>
                    Listening with care...
                </div>
            </div>
        """, unsafe_allow_html=True)
    

    
    
    # Transcript
    with st.expander("📝 View Conversation Transcript"):
        for msg in st.session_state.messages:
             st.chat_message(msg["role"]).write(msg["content"])

    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # End Session Button
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ------------------------------------------------------------------------
    # CONTROL BAR: Mic and End Session side-by-side or stacked cleanly
    # ------------------------------------------------------------------------
    if st.session_state.current_state != "Close":
         with st.container():
             col_controls_1, col_controls_2 = st.columns([1, 1], gap="medium")
             
             with col_controls_1:
                 st.markdown("<div style='text-align: center; color: #5a4a3a; font-weight: 600; margin-bottom: 0.5rem;'>Tap to Speak</div>", unsafe_allow_html=True)
                 audio_input = mic_recorder(
                     start_prompt="🎙️ Record Answer",
                     stop_prompt="⏹️ Stop Recording",
                     key='recorder',
                     format="webm"
                 )
             
             with col_controls_2:
                 st.markdown("<div style='text-align: center; color: #5a4a3a; font-weight: 600; margin-bottom: 0.5rem;'>Session Control</div>", unsafe_allow_html=True)
                 if st.button("End Session", use_container_width=True):
                     st.session_state.session_active = False
                     st.session_state.messages = []
                     st.rerun()


         # Process Audio Input (Logic stays here as it depends on audio_input existing)
         if audio_input:
             if audio_input['id'] not in st.session_state.processed_audio_ids:
                 st.session_state.processed_audio_ids.append(audio_input['id'])
                 user_text = transcribe_audio(audio_input['bytes'])
                 
                 if user_text:
                     last_user_msg = next((m for m in reversed(st.session_state.messages) if m["role"] == "user"), None)
                     
                     if not (last_user_msg and last_user_msg['content'] == user_text):
                         # Processing Animation - UPDATED TO USE CSS PULSE
                         with anim_placeholder:
                             st.markdown("""
                                 <div style='display: flex; flex-direction: column; align-items: center; 
                                 justify-content: center; padding: 2rem 0; min-height: 280px;'>
                                     <div class="processing-indicator"></div>
                                     <div style='font-family: DM Sans, sans-serif; font-size: 1.1rem; 
                                     color: #8b7355; font-weight: 500; margin-top: 1rem;'>
                                         Reflecting on your words...
                                     </div>
                                 </div>
                             """, unsafe_allow_html=True)
                         
                         time.sleep(2.0) # Increased time to ensure animation is seen
                         ai_response, is_closing = process_interaction(user_text)
                         
                         # Generating response Animation
                         with anim_placeholder:
                             st.markdown("""
                                 <div style='display: flex; flex-direction: column; align-items: center; 
                                 justify-content: center; padding: 2rem 0; min-height: 280px;'>
                                     <lottie-player 
                                         src="https://lottie.host/82df0e8d-d715-46f3-bfca-8d3ec173264c/YI13k65b9W.json" 
                                         background="transparent" 
                                         speed="1" 
                                         style="width: 200px; height: 200px;" 
                                         loop 
                                         autoplay>
                                     </lottie-player>
                                     <div style='font-family: DM Sans, sans-serif; font-size: 1.1rem; 
                                     color: #8b7355; font-weight: 500; margin-top: 1rem;'>
                                         Preparing response...
                                     </div>
                                 </div>
                             """, unsafe_allow_html=True)
                         
                         audio_bytes = generate_ai_response_audio(ai_response, st.session_state.current_voice)
                         
                         if audio_bytes:
                             with anim_placeholder:
                                 st.markdown("""
                                     <div style='display: flex; flex-direction: column; align-items: center; 
                                     justify-content: center; padding: 2rem 0; min-height: 280px;'>
                                         <lottie-player 
                                             src="https://lottie.host/6e082855-0810-444a-8742-c439164d1421/E32D5Z8X9X.json" 
                                             background="transparent" 
                                             speed="1" 
                                             style="width: 200px; height: 200px;" 
                                             loop 
                                             autoplay>
                                         </lottie-player>
                                         <div style='font-family: DM Sans, sans-serif; font-size: 1.1rem; 
                                         color: #8b7355; font-weight: 500; margin-top: 1rem;'>
                                             Speaking...
                                         </div>
                                     </div>
                                 """, unsafe_allow_html=True)
                                 st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                         
                         # Better timing for closing vs regular responses
                         word_count = len(ai_response.split())
                         if is_closing:
                             # Closing statements are longer - give more time
                             estimated_duration = max(8, word_count / 2.0) + 3
                             time.sleep(estimated_duration)
                             st.session_state.session_active = False
                             st.rerun()
                         else:
                             estimated_duration = max(3, word_count / 2.3) + 1
                             time.sleep(estimated_duration)
                             st.rerun()
    
    # ------------------------------------------------------------------------
    # HANDLE PENDING AUDIO (MOVED TO END)
    # This ensures audio logic (which sleeps) runs AFTER the grid/buttons 
    # above have been rendered by Streamlit.
    # ------------------------------------------------------------------------
    if hasattr(st.session_state, 'pending_audio') and st.session_state.pending_audio:
        # We don't want a spinner here blocking UI, just the anim placeholder above
        audio_bytes = generate_ai_response_audio(st.session_state.pending_audio, st.session_state.current_voice)
        
        if audio_bytes:
            with anim_placeholder:
                st.markdown("""
                    <div style='display: flex; flex-direction: column; align-items: center; 
                    justify-content: center; padding: 2rem 0; min-height: 280px;'>
                        <lottie-player 
                            src="https://lottie.host/6e082855-0810-444a-8742-c439164d1421/E32D5Z8X9X.json" 
                            background="transparent" 
                            speed="1" 
                            style="width: 200px; height: 200px;" 
                            loop 
                            autoplay>
                        </lottie-player>
                        <div style='font-family: DM Sans, sans-serif; font-size: 1.1rem; 
                        color: #8b7355; font-weight: 500; margin-top: 1rem;'>
                            Speaking...
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        
        text_to_speak = st.session_state.pending_audio
        word_count = len(text_to_speak.split()) if text_to_speak else 0
        estimated_duration = max(4, word_count / 2.0) + 2
        st.session_state.pending_audio = None
        
        # Block only at the very end, so UI is static and visible
        time.sleep(estimated_duration)

# Footer
st.markdown("""
    <div style='text-align: center; font-family: DM Sans, sans-serif; 
    font-size: 0.9rem; color: #a68e6c; margin-top: 3rem; padding-top: 2rem; 
    border-top: 1px solid rgba(166, 142, 108, 0.2);'>
        Powered by Ura Warriors · A safe space for reflection
    </div>
""", unsafe_allow_html=True)
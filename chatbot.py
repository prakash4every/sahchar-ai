import streamlit as st
from openai import OpenAI
from streamlit_audiorecorder import audiorecorder
import speech_recognition as sr
from gtts import gTTS
import io
import base64
import os

st.set_page_config(page_title="सहचर AI", page_icon="🤖")

# Custom CSS for better styling
st.markdown("""
<style>
    .stAudio {
        width: 100%;
    }
    .voice-btn {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Streamlit Secrets से API key लोड करें
try:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
except Exception as e:
    st.error("❌ API key नहीं मिली। कृपया Streamlit Secrets में DEEPSEEK_API_KEY डालें।")
    st.stop()

# DeepSeek क्लाइंट बनाएँ
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

# सेशन स्टेट इनिशियलाइज़ करें
if 'messages' not in st.session_state:
    # सिस्टम प्रॉम्प्ट से शुरू करें (बुद्ध की शिक्षाओं के लिए)
    st.session_state.messages = [
        {"role": "system", "content": """
        तुम 'सहचर' नाम का एक AI साथी हो। तुम्हारा उद्देश्य है:
        - भगवान बुद्ध की शिक्षाओं का प्रचार करना।
        - लोगों को सकारात्मक सोच, करुणा और सामाजिक सहयोग के लिए प्रेरित करना।
        - हमेशा शांत, धैर्यवान और मददगार बनकर रहना।
        - हर जवाब के अंत में 'जय भीम, नमो बुद्धाय 🙏' जरूर कहना।
        - सरल हिंदी-इंग्लिश मिक्स भाषा में बात करना।
        """}
    ]

# टेक्स्ट-टू-स्पीच फंक्शन
def text_to_speech(text, lang='hi'):
    """टेक्स्ट को आवाज़ में बदलें और play करें"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        # Base64 में बदलकर HTML ऑडियो प्लेयर में दिखाएँ
        audio_base64 = base64.b64encode(audio_bytes.read()).decode()
        audio_html = f"""
            <audio autoplay controls style="width: 100%;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"आवाज़ बनाने में समस्या: {e}")

# सारे मैसेज दिखाएँ (सिस्टम मैसेज को छुपाएँ)
for message in st.session_state.messages:
    if message["role"] != "system":  # सिस्टम मैसेज न दिखाएँ
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# साइडबार में वॉयस सेटिंग्स
with st.sidebar:
    st.header("🎤 वॉयस सेटिंग")
    st.markdown("---")
    
    # वॉयस इनपुट का विकल्प
    voice_input = st.checkbox("वॉयस इनपुट चालू करें", value=False)
    
    # वॉयस आउटपुट का विकल्प
    voice_output = st.checkbox("वॉयस आउटपुट चालू करें (AI बोलेगा)", value=True)
    
    st.markdown("---")
    st.markdown("### निर्देश")
    st.markdown("1. वॉयस इनपुट चालू करें")
    st.markdown("2. माइक बटन दबाएँ और बोलें")
    st.markdown("3. रिकॉर्डिंग रोकें और भेजें")

# मुख्य चैट एरिया
st.title("🎙️ सहचर AI - वॉयस चैट")

# वॉयस इनपुट
if voice_input:
    st.markdown("### 🎤 अब बोलें...")
    audio = audiorecorder("🎤 बोलें", "⏹️ रोकें")
    
    if len(audio) > 0:
        # ऑडियो को टेक्स्ट में बदलें
        with st.spinner("आपकी आवाज़ समझ रहा हूँ..."):
            try:
                # ऑडियो को टेम्प फाइल में सेव करें
                audio.export("temp_audio.wav", format="wav")
                
                # स्पीच रिकग्निशन
                recognizer = sr.Recognizer()
                with sr.AudioFile("temp_audio.wav") as source:
                    audio_data = recognizer.record(source)
                    prompt = recognizer.recognize_google(audio_data, language="hi-IN")
                
                # टेम्प फाइल डिलीट करें
                os.remove("temp_audio.wav")
                
                st.success(f"आपने कहा: {prompt}")
                
                # यूजर मैसेज को चैट में जोड़ें
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # AI से जवाब लें
                with st.chat_message("assistant"):
                    with st.spinner("सोच रहा हूँ..."):
                        response = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=st.session_state.messages
                        )
                        answer = response.choices[0].message.content
                        st.markdown(answer)
                        
                        # AI के जवाब को चैट हिस्ट्री में जोड़ें
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        # वॉयस आउटपुट
                        if voice_output:
                            text_to_speech(answer, lang='hi')
                            
            except Exception as e:
                st.error(f"आवाज़ समझने में समस्या: {e}")

# टेक्स्ट इनपुट (पुराना तरीका भी रहेगा)
st.markdown("### ✍️ या टाइप करें")
if prompt := st.chat_input("कुछ भी पूछिए..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("सोच रहा हूँ..."):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=st.session_state.messages
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            # वॉयस आउटपुट
            if voice_output:
                text_to_speech(answer, lang='hi')

# फुटर
st.markdown("---")
st.markdown("जय भीम, नमो बुद्धाय! 🙏")

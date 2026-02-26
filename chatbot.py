import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="सहचर AI", page_icon="🤖")

# Streamlit Secrets से API key लोड करें
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    st.success("✅ API key secrets से लोड हुई")
except Exception as e:
    st.error("❌ API key नहीं मिली। कृपया Streamlit Secrets में GEMINI_API_KEY डालें।")
    st.stop()

# Gemini कॉन्फ़िगर करें
genai.configure(api_key=API_KEY)

# मॉडल इनिशियलाइज़ करें (सही मॉडल नाम)
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    st.success("✅ Model लोड हो गया")
except Exception as e:
    st.error(f"❌ Model लोड करने में त्रुटि: {e}")
    st.stop()

# सेशन स्टेट इनिशियलाइज़ करें
if 'messages' not in st.session_state:
    st.session_state.messages = []

# सारे मैसेज दिखाएँ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# यूजर इनपुट
if prompt := st.chat_input("कुछ भी पूछिए..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"क्षमा करें, त्रुटि: {e}")

st.markdown("---")
st.markdown("जय भीम, नमो बुद्धाय! 🙏")

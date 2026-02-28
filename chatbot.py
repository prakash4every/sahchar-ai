import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="सहचर AI", page_icon="🤖")

# Streamlit Secrets से API key लोड करें (नाम: DEEPSEEK_API_KEY)
try:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
except Exception as e:
    st.error("❌ API key नहीं मिली। कृपया Streamlit Secrets में DEEPSEEK_API_KEY डालें।")
    st.stop()

# DeepSeek क्लाइंट बनाएँ (OpenAI-compatible)
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

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
            # DeepSeek API कॉल
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"क्षमा करें, त्रुटि: {e}")

st.markdown("---")
st.markdown("जय भीम, नमो बुद्धाय! 🙏")
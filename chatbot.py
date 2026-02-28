import streamlit as st
from openai import OpenAI

client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com/v1"
)

# चैट कॉम्प्लीशन
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": prompt}]
)
answer = response.choices[0].message.content
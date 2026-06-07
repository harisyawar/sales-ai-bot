import streamlit as st
from bot import sales_bot

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Consultant",
    page_icon="🧠",
    layout="centered"
)

# -----------------------------
# HEADER
# -----------------------------
st.title("🧠 AI Website Consultant")
st.caption("Talk to your AI strategy assistant")

# -----------------------------
# INIT SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# SIDEBAR (CHAT HISTORY STYLE)
# -----------------------------
with st.sidebar:
    st.header("📁 Session")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.write("💡 Tip:")
    st.write("Ask about website, budget, or strategy.")

# -----------------------------
# SHOW CHAT (PROPER WAY)
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# INPUT BOX (CHATGPT STYLE)
# -----------------------------
user_input = st.chat_input("Message AI Consultant...")

if user_input:

    # 1. show user message immediately
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. get AI response
    response = sales_bot(user_input)

    # 3. show AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.markdown(response)
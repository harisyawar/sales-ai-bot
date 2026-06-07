import streamlit as st
from bot import sales_bot
from state import reset_state, get_state
from memory import reset_memory


# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="AI Website Consultant",
    page_icon="🧠",
    layout="centered"
)


# ==================================================
# HEADER
# ==================================================
st.title("🧠 AI Website Consultant")
st.caption("High-ticket website strategy assistant")


# ==================================================
# SESSION INIT (CLEAN ARCHITECTURE)
# ==================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "state" not in st.session_state:
    st.session_state.state = get_state()


# ==================================================
# SIDEBAR (CONTROL PANEL)
# ==================================================
with st.sidebar:
    st.header("📁 Session Controls")

    if st.button("🗑️ Clear Chat / Reset Lead"):
        st.session_state.messages.clear()

        # FULL SYSTEM RESET (IMPORTANT FIX)
        reset_state(st.session_state.state)
        reset_memory()

        st.rerun()

    st.divider()
    st.write("💡 Tip:")
    st.write("Ask about website, business goals, or budget.")


# ==================================================
# CHAT HISTORY RENDER
# ==================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ==================================================
# INPUT BOX
# ==================================================
user_input = st.chat_input("Message AI Consultant...")


if user_input:

    # -------------------------
    # USER MESSAGE
    # -------------------------
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # -------------------------
    # LOADING UX (PRO LEVEL)
    # -------------------------
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your requirements..."):

            response = sales_bot(user_input)

            st.markdown(response)

    # -------------------------
    # SAVE ASSISTANT MESSAGE
    # -------------------------
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
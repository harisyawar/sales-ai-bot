from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from prompts import SYSTEM_PROMPT
from memory import save_memory, search_memory, reset_memory

# IMPORTANT: use your new state engine
from state import (
    get_state,
    smart_update_state,
    reset_state,
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


# ==================================================
# SESSION INIT (STREAMLIT SAFE)
# ==================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "state" not in st.session_state:
    st.session_state.state = get_state()


state = st.session_state.state
chat_history = st.session_state.chat_history


# ==================================================
# UTILS
# ==================================================
def is_question(text: str) -> bool:
    text = text.lower()
    return any(x in text for x in ["?", "how", "what", "why", "can", "which"])


def is_technical(text: str) -> bool:
    text = text.lower()
    return any(x in text for x in ["api", "frontend", "backend", "integration", "payment", "stripe"])


def should_close(user_input: str) -> bool:
    text = user_input.lower()

    exit_phrases = [
        "send proposal",
        "email me",
        "send it over",
        "we can do it on email",
        "close this",
        "i need to rush"
    ]

    # NEVER close if still asking questions
    if is_question(text):
        return False

    # close intent
    if any(p in text for p in exit_phrases):
        return True

    # close if fully qualified
    required = ["business", "goal", "budget", "timeline", "email"]
    return all(state.get(k) for k in required)


# ==================================================
# MAIN SALES BOT (PRODUCTION FLOW)
# ==================================================
def sales_bot(user_input: str):

    chat_history.append(f"User: {user_input}")

    # -------------------------
    # 1. UPDATE CRM STATE (IMPORTANT FIX)
    # -------------------------
    smart_update_state(state, user_input)

    text = user_input.lower()

    # ==================================================
    # 2. TECHNICAL MODE (EXPERT ANSWERING MODE)
    # ==================================================
    if is_technical(text):

        context = f"""
You are a senior software + sales architect.

CHAT:
{chat_history[-6:]}

STATE:
{state}

User:
{user_input}
"""

        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=context)
        ])

        chat_history.append(f"AI: {response.content}")
        save_memory(response.content)

        return response.content

    # ==================================================
    # 3. MEMORY + CONTEXT BUILD
    # ==================================================
    context = f"""
You are a high-level AI sales consultant.

Your job:
- ask natural consulting questions (NOT form questions)
- understand business deeply
- guide toward proposal
- never repeat already collected data

STATE:
{state}

CHAT HISTORY:
{chat_history[-6:]}

LONG TERM MEMORY:
{search_memory(user_input)}

User:
{user_input}
"""

    # ==================================================
    # 4. CLOSE FLOW (HIGH PRIORITY)
    # ==================================================
    if should_close(user_input):

        if state.get("completed"):
            return "We are already preparing your proposal 👍"

        if not state.get("email"):
            return "Perfect — before I prepare your proposal, what’s your email so I can send it?"

        # FINAL CLOSE RESPONSE
        state["completed"] = True

        reply = f"""
✅ Perfect — I’ve got everything needed.

📌 Project Summary:
- Business: {state.get('business')}
- Industry: {state.get('industry')}
- Goal: {state.get('goal')}
- Budget: {state.get('budget')}
- Timeline: {state.get('timeline')}

📩 Proposal will be sent to:
{state.get('email')}

We’ll now prepare your professional proposal and send it shortly 🚀

Thanks — speak soon 👋
"""

        save_memory(reply)

        # ==================================================
        # RESET EVERYTHING (CRITICAL FIX FOR YOUR BUG)
        # ==================================================
        chat_history.clear()
        reset_memory()
        reset_state(state)

        return reply

    # ==================================================
    # 5. NORMAL AI RESPONSE (SALES CONSULTANT MODE)
    # ==================================================
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=context)
    ])

    chat_history.append(f"AI: {response.content}")
    save_memory(response.content)

    return response.content
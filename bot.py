from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from state import state
from prompts import SYSTEM_PROMPT
from memory import save_memory, search_memory, update_state, update_stage, reset_memory

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

chat_history = []


# -----------------------------
# INTENT DETECTION
# -----------------------------
def is_user_still_exploring(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in ["how", "what", "why", "can", "which", "?"])


def should_close_conversation(user_input, state):

    text = user_input.lower()

    exit_phrases = [
        "send proposal",
        "email me",
        "send it over",
        "we can do it on email",
        "close this",
        "i need to rush"
    ]

    # ❌ NEVER close if user is still asking questions
    if is_user_still_exploring(text):
        return False

    # explicit close intent
    if any(p in text for p in exit_phrases):
        return True

    # implicit close only if EVERYTHING is filled
    required = ["business", "goal", "budget", "timeline", "email"]
    return all(state.get(k) for k in required)


# -----------------------------
# MAIN BOT
# -----------------------------
def sales_bot(user_input):

    chat_history.append(f"User: {user_input}")

    update_state(user_input)
    update_stage()

    text = user_input.lower()

    # ==================================================
    # 1. HANDLE TECH QUESTIONS FIRST (IMPORTANT FIX)
    # ==================================================
    if any(k in text for k in ["api", "frontend", "backend", "integration", "ticket"]):
        history_text = "\n".join(chat_history[-6:])

        context = f"""
STAGE: {state.get('stage')}

CHAT:
{history_text}

STATE:
{state}

User: {user_input}
"""

        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=context)
        ])

        chat_history.append(f"AI: {response.content}")
        save_memory(response.content)

        return response.content

    # ==================================================
    # 2. CLOSING FLOW (ONLY WHEN SAFE)
    # ==================================================
    if should_close_conversation(user_input, state):

        # prevent duplicate closing
        if state.get("completed"):
            return "We are already preparing your proposal 👍"

        # EMAIL REQUIRED GATE
        if not state.get("email"):
            return "Perfect — before I prepare your proposal, may I have your email?"

        # FINAL CLOSE
        state["completed"] = True

        reply = f"""
Perfect — I’ve got everything I need.

📌 Project Summary:
- Business: {state.get('business')}
- Goal: {state.get('goal')}
- Budget: {state.get('budget')}
- Timeline: {state.get('timeline')}

📩 Proposal will be sent to:
{state.get('email')}

We’ll prepare your full website proposal and send it shortly.

Thanks — speak soon 👋
"""

        save_memory(reply)

        # RESET SYSTEM FOR NEXT LEAD
        reset_memory()
        chat_history.clear()

        return reply

    # ==================================================
    # 3. NORMAL CONVERSATION FLOW
    # ==================================================
    history_text = "\n".join(chat_history[-6:])

    context = f"""
STAGE: {state.get('stage')}

CHAT HISTORY:
{history_text}

MEMORY:
{search_memory(user_input)}

STATE:
{state}

User: {user_input}
"""

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=context)
    ])

    chat_history.append(f"AI: {response.content}")
    save_memory(response.content)

    return response.content


# optional
REQUIRED_FIELDS = ["business", "goal", "budget", "timeline", "email"]
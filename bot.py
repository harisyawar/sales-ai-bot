from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from state import state
from prompts import SYSTEM_PROMPT

from memory import (
    save_memory,
    update_state,
    update_stage
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3
)

chat_history = []


# --------------------------------
# CLOSE DETECTION
# --------------------------------

def should_close_conversation(user_input, state):

    text = user_input.lower()

    exit_phrases = [
        "i need to rush",
        "send proposal",
        "email me",
        "send it over",
        "close this",
        "i'm busy",
        "we can do it on email",
        "send the proposal",
        "can you send proposal"
    ]

    # User explicitly wants to leave
    if any(p in text for p in exit_phrases):

        # Don't close until email exists
        return bool(state.get("email"))

    # Auto-close only when all important fields exist
    required = [
        "business",
        "goal",
        "budget",
        "email"
    ]

    return all(state.get(field) for field in required)


# --------------------------------
# MAIN SALES BOT
# --------------------------------

def sales_bot(user_input):

    # Consultation already completed
    if state.get("completed"):

        text = user_input.lower().strip()

        if text in ["thanks", "thank you", "bye", "ok", "okay"]:
            return "You're welcome. Have a great day 👋"

        return (
            "This consultation has already been completed.\n"
            "Type /reset to start a new project."
        )

    chat_history.append(f"User: {user_input}")

    update_state(user_input)
    update_stage()

    # -----------------------------
    # EMAIL MISSING BUT USER WANTS PROPOSAL
    # -----------------------------

    proposal_keywords = [
        "proposal",
        "email",
        "send",
        "rush",
        "close"
    ]

    if any(k in user_input.lower() for k in proposal_keywords):

        if not state.get("email"):

            return (
                "Perfect — I have most of the information I need 👍\n\n"
                "Before I prepare the proposal, please share your email address."
            )

    # -----------------------------
    # FINAL CLOSING
    # -----------------------------

    if should_close_conversation(user_input, state):

        state["completed"] = True

        reply = f"""
Perfect — I've got everything I need.

📌 Project Summary

Business: {state.get('business')}
Goal: {state.get('goal')}
Budget: {state.get('budget')}

📩 Proposal will be sent to:
{state.get('email')}

We’ll prepare your website proposal and send it shortly.

Thanks — speak soon 👋
"""

        save_memory(reply)

        return reply

    # -----------------------------
    # NORMAL CONSULTATION
    # -----------------------------

    history_text = "\n".join(chat_history[-10:])

    context = f"""
CURRENT STAGE:
{state.get('stage')}

CHAT HISTORY:
{history_text}

CURRENT STATE:
{state}

User:
{user_input}
"""

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=context)
    ])

    answer = response.content

    chat_history.append(f"AI: {answer}")

    save_memory(f"User: {user_input}")
    save_memory(f"AI: {answer}")

    return answer
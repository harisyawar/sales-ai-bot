from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from state import state
from prompts import SYSTEM_PROMPT
from memory import save_memory, search_memory, update_state, update_stage


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

chat_history = []

def should_close_conversation(user_input, state):
    exit_phrases = [
        "i need to rush",
        "send proposal",
        "email me",
        "we can do it on email",
        "close this",
        "i'm busy",
        "send it over"
    ]

    text = user_input.lower()

    if any(p in text for p in exit_phrases):
        return True

    required = ["business", "goal", "budget"]
    filled = sum(1 for k in required if state.get(k))

    if filled >= 3:
        return True

    return False

def sales_bot(user_input):
    if should_close_conversation(user_input, state):

        state["completed"] = True

        email = state.get("email") or "not provided"

        reply = f"""
Perfect — I’ve got everything I need.

📌 Project Summary:
- Business: {state.get('business')}
- Goal: {state.get('goal')}
- Budget: {state.get('budget')}

📩 Proposal will be sent to:
{email}

We’ll prepare your full website proposal and send it shortly.

Thanks — speak soon 👋
"""

        save_memory(reply)
        return reply
    chat_history.append(f"User: {user_input}")

    update_state(user_input)
    update_stage()

    if state.get("stage") == "closing" and not state.get("completed"):

        state["completed"] = True

        reply = f"""
Perfect — I’ve got everything I need.

We will prepare your website proposal and send it to:
{state.get('email')}

Our team will contact you shortly.

Thank you 👋
"""

        save_memory(reply)
        return reply

    history_text = "\n".join(chat_history[-6:])

    context = f"""
STAGE: {state.get('stage')}

CHAT:
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

REQUIRED_FIELDS = [
    "business",
    "goal",
    "budget",
    "timeline",
    "email"
]
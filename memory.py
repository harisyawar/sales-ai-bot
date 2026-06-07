import json
from datetime import datetime

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# IMPORTANT: no direct state import (prevents circular bugs)
from state import get_state


# ==================================================
# EMBEDDINGS ENGINE
# ==================================================
embeddings = OpenAIEmbeddings()

vector_db = FAISS.from_texts(
    ["system_init"],
    embedding=embeddings
)


# ==================================================
# MEMORY STORAGE (LONG TERM VECTOR MEMORY)
# ==================================================
def save_memory(text: str):
    """Store meaningful conversation chunks"""
    try:
        if text and len(text.strip()) > 3:
            vector_db.add_texts([text])
    except Exception as e:
        print("Memory save error:", e)


# ==================================================
# MEMORY SEARCH (CONTEXT RETRIEVAL)
# ==================================================
def search_memory(query: str):
    """Retrieve relevant past context"""
    try:
        docs = vector_db.similarity_search(query, k=3)
        return "\n\n".join([d.page_content for d in docs]) if docs else ""
    except Exception as e:
        print("Memory search error:", e)
        return ""


# ==================================================
# EXTRACTION ENGINE (CRM DATA PARSER)
# ==================================================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

EXTRACTION_PROMPT = """
You are a CRM data extraction system.

Extract ONLY valid JSON:

{
  "business": null,
  "industry": null,
  "goal": null,
  "budget": null,
  "timeline": null,
  "email": null,
  "phone": null,
  "platform": null
}

RULES:
- Extract only explicitly mentioned values
- Do NOT guess
- If missing, return null
- Email must be exact if present
- Keep response STRICT JSON ONLY (no explanation)
"""


def extract_data(user_input: str):
    """Convert user message into structured CRM data"""

    try:
        response = llm.invoke([
            SystemMessage(content=EXTRACTION_PROMPT),
            HumanMessage(content=user_input)
        ])

        return json.loads(response.content)

    except Exception as e:
        print("Extraction error:", e)
        return {}


# ==================================================
# SMART STATE UPDATER (CRM SAFE)
# ==================================================
def update_state(state: dict, user_input: str):

    data = extract_data(user_input)

    for key, value in data.items():

        if not value:
            continue

        if isinstance(value, str) and not value.strip():
            continue

        # only set once (prevents overwrite)
        if not state.get(key):
            state[key] = value


# ==================================================
# STAGE ENGINE (CRM PIPELINE LOGIC)
# ==================================================
def update_stage(state: dict):

    try:
        filled = sum([
            1 if state.get("business") else 0,
            1 if state.get("goal") else 0,
            1 if state.get("budget") else 0,
            1 if state.get("timeline") else 0,
            1 if state.get("email") else 0,
        ])

        # -------------------------
        # STAGE LOGIC
        # -------------------------
        if filled <= 2:
            state["stage"] = "discovery"

        elif filled <= 4:
            state["stage"] = "qualification"

        else:
            state["stage"] = "proposal_ready"

        # closing condition
        if state.get("email") and state.get("budget"):
            state["stage"] = "closing"

    except Exception as e:
        print("Stage update error:", e)


# ==================================================
# RESET MEMORY (CRITICAL FIX FOR STREAMLIT BUGS)
# ==================================================
def reset_memory():
    """
    Completely resets vector memory (FAISS)
    Safe for Streamlit session resets
    """

    global vector_db

    try:
        vector_db = FAISS.from_texts(
            ["system_init"],
            embedding=embeddings
        )
    except Exception as e:
        print("Memory reset error:", e)


# ==================================================
# FULL CRM RESET (OPTIONAL ADVANCED USE)
# ==================================================
def reset_full_system(state: dict):
    """
    Resets both CRM state + memory
    """

    try:
        state.clear()
        state.update(get_state())
        reset_memory()

    except Exception as e:
        print("Full reset error:", e)
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json

from state import state

# -------------------------
# EMBEDDINGS + VECTOR DB
# -------------------------
embeddings = OpenAIEmbeddings()

vector_db = FAISS.from_texts(
    ["system_init"],
    embedding=embeddings
)


def save_memory(text: str):
    """Store conversation in vector DB"""
    vector_db.add_texts([text])


def search_memory(query: str):
    """Retrieve relevant memory"""
    try:
        docs = vector_db.similarity_search(query, k=3)
        return "\n\n".join([d.page_content for d in docs]) if docs else ""
    except Exception as e:
        print("Memory error:", e)
        return ""


# -------------------------
# EXTRACTION LLM
# -------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


EXTRACTION_PROMPT = """
Extract structured JSON ONLY:

{
  "business": null,
  "goal": null,
  "platform": null,
  "budget": null,
  "timeline": null,
  "email": null,
  "phone": null
}

RULES:
- Extract only if clearly mentioned
- If not present, return null
- Email must be exact if present
"""


# -------------------------
# SAFE JSON PARSER
# -------------------------
def extract_data(user_input: str):

    try:
        response = llm.invoke([
            SystemMessage(content=EXTRACTION_PROMPT),
            HumanMessage(content=user_input)
        ])

        return json.loads(response.content)

    except Exception as e:
        print("Extraction error:", e)
        return {}


# -------------------------
# STATE UPDATER
# -------------------------
def update_state(user_input: str):

    data = extract_data(user_input)

    for k, v in data.items():

        if not v:
            continue

        # normalize empty strings
        if isinstance(v, str) and v.strip() == "":
            continue

        # only update if not already set
        if not state.get(k):
            state[k] = v


# -------------------------
# STAGE ENGINE (SAFE)
# -------------------------
def update_stage():

    try:
        if state.get("business") and state.get("goal") and state.get("budget"):
            state["stage"] = "consultation"

        if state.get("email") and state.get("phone"):
            state["stage"] = "closing"

    except Exception as e:
        print("Stage error:", e)
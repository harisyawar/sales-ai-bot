from datetime import datetime
import uuid


# ==================================================
# STATE FACTORY (NEW LEAD)
# ==================================================
def get_state():
    return {
        # -------------------------
        # IDENTIFICATION
        # -------------------------
        "lead_id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat(),

        # -------------------------
        # CORE BUSINESS INFO (DYNAMIC)
        # -------------------------
        "business": None,
        "industry": None,
        "goal": None,
        "requirements": None,

        # -------------------------
        # PROJECT PARAMETERS
        # -------------------------
        "budget": None,
        "timeline": None,
        "platform": None,

        # -------------------------
        # CONTACT INFO
        # -------------------------
        "email": None,
        "phone": None,
        "name": None,

        # -------------------------
        # SALES INTELLIGENCE
        # -------------------------
        "stage": "discovery",   # discovery → qualification → proposal → closing → completed
        "intent_score": 0,
        "lead_quality": "cold",  # cold / warm / hot

        # -------------------------
        # CONTROL FLAGS
        # -------------------------
        "completed": False,
        "handoff_required": False,

        # prevents repetition + improves UX
        "locked_fields": set(),
        "asked_fields": set(),

        # conversation control
        "last_question": None,
    }


# ==================================================
# FIELD LOCKING (ANTI-REPEAT ENGINE)
# ==================================================
def lock_field(state: dict, field: str, value):

    if value and not state.get(field):
        state[field] = value
        state["locked_fields"].add(field)


# ==================================================
# TRACK ASKED QUESTIONS (UX CONTROL)
# ==================================================
def mark_asked(state: dict, field: str):
    state["asked_fields"].add(field)


def already_asked(state: dict, field: str) -> bool:
    return field in state["asked_fields"]


# ==================================================
# INTENT SCORING (SALES QUALIFICATION ENGINE)
# ==================================================
def update_intent_score(state: dict, text: str):

    text = text.lower()

    # buying signals
    if any(k in text for k in ["buy", "price", "cost", "budget", "quote", "proposal"]):
        state["intent_score"] += 10

    # urgency signals
    if any(k in text for k in ["now", "urgent", "asap", "this week", "today"]):
        state["intent_score"] += 15

    # business seriousness signals
    if any(k in text for k in ["start", "build", "launch", "setup"]):
        state["intent_score"] += 10

    # classify lead
    if state["intent_score"] >= 70:
        state["lead_quality"] = "hot"
    elif state["intent_score"] >= 40:
        state["lead_quality"] = "warm"
    else:
        state["lead_quality"] = "cold"


# ==================================================
# STAGE ENGINE (CRM PIPELINE)
# ==================================================
def update_stage(state: dict):

    filled = sum([
        1 if state.get("business") else 0,
        1 if state.get("goal") else 0,
        1 if state.get("budget") else 0,
        1 if state.get("timeline") else 0,
        1 if state.get("email") else 0,
    ])

    if filled <= 2:
        state["stage"] = "discovery"

    elif filled <= 4:
        state["stage"] = "qualification"

    else:
        state["stage"] = "proposal_ready"

    # closing condition
    if state.get("email") and state.get("budget"):
        state["stage"] = "closing"


# ==================================================
# SMART STATE UPDATE (DOMAIN-AGNOSTIC)
# ==================================================
def smart_update_state(state: dict, user_input: str):

    text = user_input.lower()

    # -------------------------
    # BUSINESS / CONTEXT
    # -------------------------
    if any(k in text for k in ["company", "business", "startup", "agency"]):
        lock_field(state, "business", user_input)

    # -------------------------
    # INDUSTRY DETECTION (GENERIC)
    # -------------------------
    industries = [
        "travel", "ecommerce", "education", "real estate",
        "health", "finance", "saas", "agency", "logistics"
    ]
    for ind in industries:
        if ind in text:
            lock_field(state, "industry", ind)

    # -------------------------
    # GOAL DETECTION
    # -------------------------
    if any(k in text for k in ["leads", "sales", "bookings", "revenue", "conversion"]):
        lock_field(state, "goal", user_input)

    # -------------------------
    # BUDGET DETECTION (GENERIC)
    # -------------------------
    if any(char.isdigit() for char in text):
        if any(k in text for k in ["$", "usd", "rs", "rupees"]):
            lock_field(state, "budget", user_input)

    # -------------------------
    # TIMELINE DETECTION
    # -------------------------
    if any(k in text for k in ["day", "days", "week", "month"]):
        lock_field(state, "timeline", user_input)

    # -------------------------
    # EMAIL DETECTION
    # -------------------------
    if "@" in text:
        lock_field(state, "email", user_input.strip())

    # -------------------------
    # INTELLIGENCE UPDATE
    # -------------------------
    update_intent_score(state, user_input)

    # update pipeline
    update_stage(state)


# ==================================================
# NEXT BEST QUESTION ENGINE (OPTIONAL USE IN BOT)
# ==================================================
def next_question(state: dict):

    flow = ["business", "industry", "goal", "budget", "timeline", "email"]

    questions = {
        "business": "Tell me a bit about your business so I can understand your needs better.",
        "industry": "Which industry are you operating in?",
        "goal": "What is your main goal for this project?",
        "budget": "What budget range are you considering for this?",
        "timeline": "What timeline are you targeting for launch?",
        "email": "Where should I send the proposal?"
    }

    for field in flow:
        if not state.get(field):
            return questions[field]

    return None


# ==================================================
# RESET (NEW LEAD CLEANUP - IMPORTANT FOR STREAMLIT)
# ==================================================
def reset_state(state: dict):
    state.clear()
    state.update(get_state())
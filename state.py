# -----------------------------
# GLOBAL CRM STATE
# -----------------------------

state = {
    "business": None,
    "goal": None,
    "platform": None,   # Shopify / WordPress / Custom CMS
    "budget": None,
    "timeline": None,
    "email": None,
    "phone": None,
    "stage": "discovery",
    "completed": False
}


# -----------------------------
# RESET FUNCTION
# -----------------------------

def reset_state():
    state.clear()
    state.update({
        "business": None,
        "goal": None,
        "platform": None,
        "budget": None,
        "timeline": None,
        "email": None,
        "phone": None,
        "stage": "discovery",
        "completed": False
    })
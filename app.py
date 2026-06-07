from bot import sales_bot
from state import reset_state

while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    if user_input.lower() == "/reset":
        reset_state()
        print("AI: reset done")
        continue

    print("AI:", sales_bot(user_input))
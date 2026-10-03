"""What does the model actually see when you give it a tool? No API key needed.

Run:    python 04_tool_demo.py

An agent never sees your Python code. It sees three things: the tool's NAME,
its DESCRIPTION (your docstring) and the ARGUMENTS it takes. That is all it has
to decide whether and how to call the tool, so the docstring matters.
"""
from langchain_core.tools import tool


@tool
def categorize_expense(amount: float, item_description: str) -> str:
    """Decide whether an expense is CapEx (a lasting asset) or OpEx (a running cost)."""
    return "CapEx" if amount > 5000 else "OpEx"


print("name       :", categorize_expense.name)
print("description:", categorize_expense.description)
print("arguments  :", categorize_expense.args)
print()

# You can call a tool yourself, exactly as an agent would:
print("call result:", categorize_expense.invoke({"amount": 480000, "item_description": "PLC controllers"}))

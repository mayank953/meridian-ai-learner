# 12 · Agents explained

RAG **answers questions**. An **agent** **does work**: it decides which tools to use, looks at the results, and continues until it can answer.

---

## 1. The words

| Word | Plain meaning | Analogy |
|---|---|---|
| **Tool** | A small Python function the AI is allowed to run | A thermometer in the chef's hand |
| **Prompt** (system prompt) | The standing instructions: role, tasks, how to decide, how to answer | A job description |
| **Agent** | AI + tools + prompt, working in a loop: *think → use a tool → read the result → think again → answer* | A chef who can measure, taste and adjust |
| **Supervisor** | Plain Python code that runs several agents and combines their work | The head of the team |

## 2. How this project's audit works

```
purchase request
      │
      ├─► Risk agent     (tools: sanctions check, credit score)   ─► report 1 ┐
      ├─► Tax agent      (tools: tax calculator, exchange rate)   ─► report 2 ├─► CFO step ─► memo
      └─► Control agent  (tool: expense classifier)               ─► report 3 ┘
```

The three agents run **one after another** (they could run in parallel; one after another is easier to read and follow in the logs). The CFO step is **one AI call without tools**.

## 3. The tools (`agent/tools.py`)

```python
@tool
def categorize_expense(amount: float, item_description: str) -> str:
    """Determines if the expense is Capital Expenditure (CapEx) or Operational (OpEx) using accounting standards."""
```

The AI never sees your Python code. It sees only three things: the tool's **name**, its **description** (the docstring) and its **arguments**. That is all it has to decide *whether* and *how* to call it, so write docstrings clearly. See it yourself: `python docs/examples/04_tool_demo.py`.

| Tool | Used by | Facts come from |
|---|---|---|
| `check_sanctions_list` | Risk | AI's general knowledge |
| `get_vendor_credit_score` | Risk | AI's general knowledge (unknown vendor → 45) |
| `calculate_cross_border_tax` | Tax | AI's general knowledge |
| `validate_fx_hedge` | Tax | **Live exchange-rate website**; the AI only if the site fails |
| `categorize_expense` | Control | AI's general knowledge |

> Four of the five tools ask the AI instead of a real database. This keeps the demo free of extra accounts. A real system would call a sanctions-screening service, a credit bureau and a tax engine.

If a tool's AI call fails, it returns `SYSTEM WARNING … Manual review required` instead of crashing the whole audit. Check the logs when you see such text.

## 4. The prompts (`agent/prompts.py`)

Each of the three agent prompts has the same four parts:

1. **Role**: *"You are a Senior Risk & Compliance Officer…"*
2. **Responsibilities**: what you must do
3. **Decision framework**: *"Run `check_sanctions_list` first. A RED ALERT means immediate rejection. Then run `get_vendor_credit_score`; a score of 75 or more is low risk…"*
4. **Output format**: the exact layout

The fixed layout is important: the next step can rely on it. The CFO prompt looks for these exact words in the reports:

| Word found | Final decision |
|---|---|
| `RED ALERT` | **REJECTED** |
| `FX ALERT` or `HOLD FOR TREASURY AUDIT` | **CONDITIONAL HOLD** |
| all `APPROVED` / `SUCCESS` | **APPROVED TO PAY** |

If you rename one of these words, rename it everywhere.

## 5. The code (`agent/agents.py`)

Creating an agent is one call:

```python
from langchain.agents import create_agent

def create_specialized_agent(tools, system_prompt):
    return create_agent(model=get_llm(), tools=tools, system_prompt=system_prompt)
```

The supervisor makes three:

```python
self.risk_agent    = create_specialized_agent([check_sanctions_list, get_vendor_credit_score], RISK_AGENT_PROMPT)
self.tax_agent     = create_specialized_agent([calculate_cross_border_tax, validate_fx_hedge], TAX_AGENT_PROMPT)
self.control_agent = create_specialized_agent([categorize_expense], CONTROL_AGENT_PROMPT)
```

and `run_audit()` runs them, then asks for the memo:

```python
risk_result    = self._invoke_agent(self.risk_agent, request)
tax_result     = self._invoke_agent(self.tax_agent, request)
control_result = self._invoke_agent(self.control_agent, request)
cfo_memo = extract_text(self.llm.invoke(SYNTHESIS_PROMPT_TEMPLATE.format(...)).content)
```

Calling an agent means giving it a list of messages and reading the last one:

```python
result = agent.invoke({"messages": [{"role": "user", "content": request}]})
text = extract_text(result["messages"][-1].content)
```

### LangChain and LangGraph
`create_agent` is LangChain's standard way to build an agent. Under the hood it runs on **LangGraph**, which is why `langgraph` is in `requirements.txt` and may appear in logs. This project writes no LangGraph code. You would use LangGraph directly when you need loops, branches or approval steps that a simple agent can't express.

## 6. What to expect from the output

- The AI writes the text, so **wording changes** from run to run. The **layout** and key words should stay stable.
- Temperature `0` (the default) makes answers more repeatable. If a model repeats itself, try `LLM_TEMPERATURE=1.0`.
- An AI can be wrong. Real audits keep a person in the loop.

## 7. Run the supervisor without the web server

From the `backend/` folder:

```bash
cd backend
GOOGLE_API_KEY=your-key python -m agent.agents
```

(This does not read `.env`, because `.env` lives in the main folder. So pass the key like this.)

## 8. Try it

1. Add a sixth tool, `check_delivery_risk(country: str)`, and give it to the Control agent.
2. Change the `75` threshold in `RISK_AGENT_PROMPT` and run the same request.
3. Use `1 EUR = 190 JPY` and read the CFO memo.
4. Delete the "output format" part of one prompt and see how the result changes.

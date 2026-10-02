import json
import requests
from langchain_core.tools import tool
from typing import Dict
from rag.llm import extract_text, get_llm
from logger import GLOBAL_LOGGER as log


# ==========================================
# INTERNAL LLM HELPER
# ==========================================

def _ask_llm(prompt: str) -> str:
    """Invoke the configured LLM and return the text content."""
    try:
        response = get_llm().invoke(prompt)
        return extract_text(response.content)
    except Exception as e:
        return f"LLM_ERROR: {str(e)}"


# ==========================================
# STEP 1: DEFINE DYNAMIC TOOLSETS
# ==========================================

# --- Agent 1 Tools: Risk & Compliance ---

@tool
def check_sanctions_list(vendor_name: str) -> str:
    """Checks if a vendor is on global restricted/sanctioned entities lists."""
    prompt = f"""You are a compliance screening system. Your job is to check whether the 
vendor name below appears on any major global sanctions or restricted-entity lists based 
on your training knowledge.

Check against these lists:
- US OFAC SDN (Specially Designated Nationals) List
- EU Consolidated Sanctions List
- UN Security Council Sanctions List
- UK HMT Sanctions List
- Any other major international sanctions or embargo lists

Vendor to screen: "{vendor_name}"

INSTRUCTIONS:
- If the vendor name matches or closely resembles ANY known sanctioned entity, respond 
  with: RED ALERT: [reason and which list they appear on]
- If the vendor is NOT found on any known sanctions list, respond with: 
  CLEARED: Vendor not found on known global sanctions lists.
- If the name is suspicious or could be a shell company for a sanctioned entity, note 
  that concern.
- Be precise. Do not fabricate matches — only flag if you have genuine knowledge.

Respond in a single concise paragraph starting with either "RED ALERT:" or "CLEARED:"."""

    result = _ask_llm(prompt)
    if result.startswith("LLM_ERROR"):
        return f"SYSTEM WARNING: Sanctions check unavailable — {result}. Manual review required."
    return result


@tool
def get_vendor_credit_score(vendor_name: str) -> str:
    """Retrieves vendor creditworthiness assessment based on publicly known financial health signals."""
    prompt = f"""You are a financial credit assessment system. Provide a credit score 
estimate (0-100) for the vendor below based on your training knowledge.

Vendor: "{vendor_name}"

ASSESSMENT CRITERIA:
- Company size, age, and market presence
- Industry reputation and stability
- Any known financial difficulties, bankruptcies, or controversies
- Public financial data or credit ratings if known (e.g., Dun & Bradstreet, S&P)
- Country of incorporation and regulatory environment

RESPONSE FORMAT (strict JSON):
{{
    "score": <integer 0-100>,
    "risk_level": "<LOW/MODERATE/HIGH>",
    "reasoning": "<brief explanation of score factors>"
}}

SCORING GUIDE:
- 75-100: Well-known, financially stable company → LOW risk
- 50-74: Mid-tier or limited public data → MODERATE risk  
- 0-49: Unknown, controversial, or financially distressed → HIGH risk

If the vendor is completely unknown, assign a score of 45 (MODERATE-HIGH risk) and note 
that insufficient data is available.

Respond ONLY with the JSON object, no other text."""

    result = _ask_llm(prompt)
    if result.startswith("LLM_ERROR"):
        return f"SYSTEM WARNING: Credit check unavailable — {result}. Manual review required."

    # Try to parse and format nicely
    try:
        # Strip markdown code fences if present
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]  # Remove first line
            cleaned = cleaned.rsplit("```", 1)[0]  # Remove last fence
            cleaned = cleaned.strip()
        data = json.loads(cleaned)
        score = data.get("score", "N/A")
        risk = data.get("risk_level", "UNKNOWN")
        reasoning = data.get("reasoning", "No details available")
        return f"CREDIT SCORE: {score}/100 | RISK: {risk} | {reasoning}"
    except (json.JSONDecodeError, KeyError):
        # Return raw LLM response if parsing fails
        return result


# --- Agent 2 Tools: Tax & Treasury ---

@tool
def calculate_cross_border_tax(amount: float, origin: str, destination: str) -> Dict:
    """Calculates VAT/GST and Import Duties for cross-border transactions."""
    prompt = f"""You are an international tax calculation system. Calculate the applicable 
taxes for the following cross-border transaction:

- Transaction Amount: {amount:,.2f}
- Origin Country: {origin}
- Destination Country: {destination}

CALCULATE:
1. The standard VAT/GST rate applicable in the destination country
2. Any applicable import duties for the product category (use general merchandise rate)
3. Consider any bilateral trade agreements between origin and destination
4. The combined effective tax rate

RESPONSE FORMAT (strict JSON):
{{
    "tax_rate": <decimal between 0 and 1, e.g. 0.18>,
    "vat_gst_rate": <decimal>,
    "import_duty_rate": <decimal>,
    "tax_amount": <float, amount * tax_rate>,
    "vat_gst_amount": <float>,
    "import_duty_amount": <float>,
    "total_cost": <float, original amount + total tax>,
    "trade_agreement_notes": "<any relevant trade agreement info>",
    "route": "{origin}_{destination}"
}}

Use current standard rates based on your training knowledge. Be accurate — these numbers 
affect financial decisions.

Respond ONLY with the JSON object, no other text."""

    result = _ask_llm(prompt)
    if result.startswith("LLM_ERROR"):
        return {"error": result, "route": f"{origin}_{destination}"}

    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()
        data = json.loads(cleaned)
        # Ensure required keys exist
        data.setdefault("route", f"{origin}_{destination}")
        data.setdefault("tax_amount", amount * data.get("tax_rate", 0.15))
        data.setdefault("rate", data.get("tax_rate", 0.15))
        return data
    except (json.JSONDecodeError, KeyError):
        # Fallback: return a safe dict with the raw response
        return {
            "tax_amount": amount * 0.15,
            "rate": 0.15,
            "route": f"{origin}_{destination}",
            "note": "Fallback rate used — LLM response could not be parsed",
            "raw_response": result,
        }


@tool
def validate_fx_hedge(currency_pair: str, rate_used: float) -> str:
    """Checks if the FX rate used matches the current market rate, with a 5% variance threshold."""

    base, quote = None, None
    # Parse currency pair like "EUR_INR" or "USD_INR"
    parts = currency_pair.upper().replace("/", "_").replace("-", "_").split("_")
    if len(parts) == 2:
        base, quote = parts[0], parts[1]

    market_rate = None

    # --- Attempt 1: Live rate from Frankfurter API ---
    if base and quote:
        try:
            url = f"https://api.frankfurter.dev/v1/latest?base={base}&symbols={quote}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                market_rate = data.get("rates", {}).get(quote)
        except Exception:
            pass  # Fall through to LLM fallback

    # --- Attempt 2: LLM fallback for rate estimation ---
    if market_rate is None:
        prompt = f"""What is the approximate current exchange rate for {currency_pair.replace('_', '/')}?
Respond with ONLY a single number (the rate). For example, if 1 EUR = 91.5 INR, respond: 91.5"""
        llm_result = _ask_llm(prompt)
        try:
            market_rate = float(llm_result.strip())
        except ValueError:
            return f"FX WARNING: Unable to determine market rate for '{currency_pair}'. Manual Treasury review required. (API and LLM both unavailable)"

    # --- Calculate variance ---
    variance = abs(rate_used - market_rate) / market_rate
    source = "live market" if base and quote else "estimated"

    if variance > 0.05:
        return (
            f"FX ALERT: Rate used ({rate_used}) vs {source} rate ({market_rate:.4f}) — "
            f"Variance {variance:.2%} EXCEEDS 5% limit. Audit required before payment release."
        )
    return (
        f"FX SUCCESS: Rate used ({rate_used}) vs {source} rate ({market_rate:.4f}) — "
        f"Variance {variance:.2%} is within acceptable 5% hedge band."
    )


# --- Agent 3 Tools: Financial Control ---

@tool
def categorize_expense(amount: float, item_description: str) -> str:
    """Determines if the expense is Capital Expenditure (CapEx) or Operational (OpEx) using accounting standards."""
    prompt = f"""You are a financial controller applying GAAP/IFRS accounting standards.
Classify the following expense:

- Amount: {amount:,.2f}
- Item Description: "{item_description}"

CLASSIFICATION RULES (GAAP/IFRS):
- CapEx: Assets with useful life > 1 year, that provide future economic benefit.
  Examples: servers, machinery, buildings, vehicles, large software licenses.
  → Must be capitalized on the balance sheet and depreciated.
  
- OpEx: Day-to-day operational costs consumed within the period.
  Examples: office supplies, SaaS subscriptions, repairs, utilities, travel.
  → Deducted immediately in the P&L.

ADDITIONAL CHECKS:
- If CapEx and amount > 500,000: Flag for additional CFO sign-off
- If classified as OpEx but amount > 100,000: Flag as possible misclassification
- Suggest depreciation period if CapEx (standard periods: IT equipment 3-5 years, 
  machinery 5-10 years, buildings 20-40 years)

RESPONSE FORMAT:
CLASSIFICATION: [CapEx / OpEx]
REASONING: [why this classification applies]
DEPRECIATION: [if CapEx: X years | if OpEx: N/A]
FLAGS: [any anomaly flags or sign-off requirements, or "None"]

Respond in this exact format, nothing else."""

    result = _ask_llm(prompt)
    if result.startswith("LLM_ERROR"):
        # Conservative fallback: use simple heuristic
        if amount > 50000 or any(
            kw in item_description.lower()
            for kw in ["server", "machine", "vehicle", "building", "equipment", "hardware"]
        ):
            return "CLASSIFICATION: CapEx (Depreciate over 3 years) — [Fallback: LLM unavailable, heuristic used]"
        return "CLASSIFICATION: OpEx (Immediate deduction) — [Fallback: LLM unavailable, heuristic used]"
    return result

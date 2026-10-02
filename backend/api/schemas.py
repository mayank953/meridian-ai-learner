from pydantic import BaseModel


# ============================================================
# AGENT  Schemas
# ============================================================



class AuditRequest(BaseModel):
    request_text: str

class AuditResponse(BaseModel):
    risk_result: str
    tax_result: str
    control_result: str
    cfo_memo: str


# ============================================================
# RAG  Schemas
# ============================================================


class QueryRequest(BaseModel):
    query: str
    retriever_type: str = "similarity"

class QueryResponse(BaseModel):
    answer: str
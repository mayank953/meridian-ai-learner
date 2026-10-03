"""FastAPI in one small file. No cloud account needed.

Run:    uvicorn 01_fastapi_hello:app --reload --port 8001      (from this folder)
Then open:  http://localhost:8001/docs

Try in /docs:
  1. GET  /hello                      -> a plain JSON reply
  2. GET  /hello/Asha?shout=true      -> a path parameter and a query parameter
  3. POST /orders  with {"item": "servo motor", "quantity": 2}   -> validated body
  4. POST /orders  with {"item": "servo motor"}                  -> 422: quantity is missing
  5. POST /orders  with {"item": "x", "quantity": -5}            -> 422: must be greater than 0
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="FastAPI hello")


class OrderRequest(BaseModel):
    """The shape of the data we expect. FastAPI checks every request against it."""
    item: str
    quantity: int = Field(gt=0, description="Must be greater than zero")


class OrderResponse(BaseModel):
    message: str
    total_items: int


@app.get("/hello")
def hello():
    return {"message": "hello"}


@app.get("/hello/{name}")
def hello_name(name: str, shout: bool = False):
    # {name} comes from the URL path; shout comes from ?shout=true in the query string
    text = f"hello {name}"
    return {"message": text.upper() if shout else text}


@app.post("/orders", response_model=OrderResponse)
def create_order(order: OrderRequest):
    if order.item.strip().lower() == "forbidden":
        # HTTPException turns into a proper HTTP error response
        raise HTTPException(status_code=400, detail="That item cannot be ordered")
    return OrderResponse(message=f"Ordered {order.quantity} x {order.item}", total_items=order.quantity)
